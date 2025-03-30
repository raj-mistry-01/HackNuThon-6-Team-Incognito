import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ForgotPasswordNavigationTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    def locate_element(self, selectors, wait_time=10):
        wait = WebDriverWait(self.driver, wait_time)
        for selector_type, selector_value in selectors.items():
            if not selector_value:
                continue
            try:
                if selector_type == "id" and selector_value:
                    return wait.until(EC.presence_of_element_located((By.ID, selector_value)))
                elif selector_type == "css" and selector_value:
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_value)))
                elif selector_type == "xpath" and selector_value:
                    return wait.until(EC.presence_of_element_located((By.XPATH, selector_value)))
                elif selector_type == "name" and selector_value:
                    return wait.until(EC.presence_of_element_located((By.NAME, selector_value)))
            except Exception:
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")

    def test_forgot_password_navigation(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "testcase.json"), "r") as f:
                test_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            test_data = {}  # Use default values if file not found or empty

        # Handle multiple test data sets if available
        test_cases = test_data.get("test_cases", [{}]) # Default to a list with an empty dict if no test cases

        for test_case in test_cases:
            try:
                self.driver.get("https://github.com/login")

                # Step 1: Click the 'Forgot password?' link
                forgot_password_link = self.locate_element(test_case.get("elements", [{"selectors": {"id": "forgot-password"}}])[0].get("selectors", {"id": "forgot-password"}))
                forgot_password_link.click()

                # Expected Result 1: User is redirected to the password reset page.
                self.assertEqual(self.driver.current_url, "https://github.com/password_reset")
                print("Test Passed")
                test_result = True

            except Exception as e:
                print(f"Test Failed: {e}")
                test_result = False
                # Add more detailed error handling/reporting if needed
            
            if not test_result: # Exit if any test case fails
                return False

        return True # Return True if all test cases pass


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ForgotPasswordNavigationTest))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise