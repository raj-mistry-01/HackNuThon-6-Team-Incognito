from flask import Flask, jsonify, send_file , request
import json
import os
import subprocess
import threading
import requests
from thread_batch import main_fn
from flask_cors import CORS  # Import CORS
from server import fetch_ci_file, push_updated_ci_file, trigger_pipeline , wait_for_commit

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://incognito-three-chi.vercel.app"}})

# ✅ Local File Paths
TEST_CASES_FILE = "test_cases.json"       # Test case file (local)
SELENIUM_SCRIPT_FILE = "test_runner.py"   # Selenium script file (local)
REPORT_FILE = "report.json"               # Report output file

test_status = False

@app.route("/testing" , methods = ["GET"])
def testing():
    return jsonify( {"rah" : " eaj"})


# ✅ Trigger Selenium Tests
def run_tests(WEBSITE_URL):
    global test_status

    try:
        print("🔥 Running Main Function to Fetch Test Files...")
        
        # ✅ Execute main_fn() to clone the Git repo and generate the `git` folder
        main_fn(WEBSITE_URL=WEBSITE_URL)
        
        # ✅ Define the path to the dynamically created `run_all_tests.py`
        repo_folder = os.path.join(os.getcwd(), "git")
        test_script = os.path.join(repo_folder, "run_all_tests.py")

        # ✅ Check if the script exists before executing
        if os.path.exists(test_script):
            print(f"✅ Found `run_all_tests.py` at: {test_script}")
            
            # ✅ Execute the test script dynamically
            result = subprocess.run(
                ["python", test_script],
                capture_output=True,
                text=True
            )

            # ✅ Print the script output
            print("\n🔥 `run_all_tests.py` Output:")
            print(result.stdout)
            print("\n❌ `run_all_tests.py` Errors (if any):")
            print(result.stderr)

            # ✅ Check if the test script executed successfully
            if result.returncode == 0:
                print("✅ `run_all_tests.py` executed successfully.")
                test_status = True  # All tests passed
            else:
                print("❌ `run_all_tests.py` failed with errors.")
                test_status = False

        else:
            print("❌ `run_all_tests.py` not found in the `git` folder.")
            test_status = False

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_status = False


# 🔥 Automatically run tests when the server starts
def run_tests_on_startup():
    print("\n🚀 Automatically triggering tests on server startup...")
    run_tests()


# 🔥 Endpoint to trigger tests (manual trigger)
@app.route('/run-tests', methods=['GET'])
def trigger_tests():
    run_tests()
    return jsonify({"message": "Test execution completed. Check the report."})


# 🔥 Simplified `/test-status` endpoint → Only sends `true` or `false`
@app.route('/test-status', methods=['POST'])
def get_test_status():
    # WEBSITE_URL = "https://github.com/login"
    data = request.get_json()
    wrl = data["WEBSITE_URL"]
    # ✅ Execute `main_fn()` + `run_all_tests.py`
    run_tests(WEBSITE_URL=wrl)

    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            report = json.load(f)

        # ✅ Use the correct field names
        total_tests = report.get("total_tests", 0)
        passed_tests = report.get("passed_tests", 0)  # Correct field name

        # ✅ Only return status: true or false
        status = total_tests == passed_tests
        if push_updated_ci_file(status):
            # ✅ Wait for the new YAML commit
            commit_message = f"🔥 Add {'SUCCESS' if status else 'FAIL'} pipeline YAML"

            if wait_for_commit(commit_message):
                pipeline_triggered = trigger_pipeline()
                return jsonify({
                    "status": status,
                    "pipeline_triggered": pipeline_triggered
                })

    # ✅ If no report is found, return false status
    return jsonify({"status": False, "pipeline_triggered": False})

# 🔥 Endpoint to serve the test report file
@app.route('/report', methods=['GET'])
def get_report():
    if os.path.exists(REPORT_FILE):
        return send_file(REPORT_FILE, as_attachment=True)
    return jsonify({"error": "Report not found"}), 404



if __name__ == '__main__':
    # 🔥 Start the server with tests running in a separate thread
    # threading.Thread(target=run_tests_on_startup).start()
    app.run(debug=True, port=5000)
