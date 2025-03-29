import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# ✅ Specify the Testing Domain
DOMAIN = "https://incognito-three-chi.vercel.app/login"

# ✅ Load test cases from JSON file
with open("test_cases.json", "r") as f:
    test_cases = json.load(f)["test_cases"]

# ✅ Initialize the Chrome driver
driver = webdriver.Chrome()

# ✅ Run all test cases dynamically
results = []

try:
    for i, case in enumerate(test_cases, start=1):
        print(f"\n🔥 Running Test Case {i}/{len(test_cases)}")

        # 1. Open the Login Page
        driver.get(DOMAIN)
        time.sleep(2)

        # 2. Fill the form with test case data
        driver.find_element(By.ID, "email").send_keys(case["email"])
        driver.find_element(By.ID, "password").send_keys(case["password"])

        # 3. Click the login button
        driver.find_element(By.ID, "login").click()
        time.sleep(3)

        # ✅ Validate the result
        current_url = driver.current_url
        if case["expected_url"] in current_url:
            print(f"✅ Test {i} PASSED: {current_url}")
            results.append({"test_case": i, "status": "PASSED", "url": current_url})
        else:
            print(f"❌ Test {i} FAILED: {current_url}")
            results.append({"test_case": i, "status": "FAILED", "url": current_url})

except Exception as e:
    print(f"❌ Exception occurred: {str(e)}")

finally:
    driver.quit()


# ✅ Generate the JUnit XML report
import subprocess
subprocess.run(["python", "report_generator.py"])

# ✅ Print Final Results Summary
print("\n🚀 Test Execution Summary:")
for res in results:
    print(f"Test {res['test_case']}: {res['status']} → {res['url']}")