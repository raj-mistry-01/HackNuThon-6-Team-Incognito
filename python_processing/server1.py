from flask import Flask, jsonify, send_file
import os

app = Flask(__name__)

# ✅ Path to test cases and Selenium script
TEST_CASES_PATH = os.path.join(os.getcwd(), "test_cases.json")
SELENIUM_SCRIPT_PATH = os.path.join(os.getcwd(), "sel.py")


@app.route('/test' , methods=['GET'])
def test_() :
    return jsonify({"ok" : "ok"})

# 🔥 API to serve test cases
@app.route('/test-cases', methods=['GET'])
def get_test_cases():
    if os.path.exists(TEST_CASES_PATH):
        return send_file(TEST_CASES_PATH, as_attachment=True)
    return jsonify({"error": "Test cases not found"}), 404

# 🔥 API to serve Selenium script
@app.route('/selenium-script', methods=['GET'])
def get_selenium_script():
    if os.path.exists(SELENIUM_SCRIPT_PATH):
        return send_file(SELENIUM_SCRIPT_PATH, as_attachment=True)
    return jsonify({"error": "Selenium script not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
