import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestForgotPasswordNavigation(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_data = self.load_test_data()

    def tearDown(self):
        self.driver.quit()

    def load_test_data(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "testcase.json"), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
            return {}  # Return empty dict for default behavior

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
            # If test data is available, iterate through it
            if self.test_data:
                for test_case in self.test_data.get("test_cases", []):  # Handle missing "test_cases" key
                    self.run_test(test_case)
            else:
                # Run with default values if no test data
                self.run_test({}) # Pass empty dict for default behavior
            return True # Return True if all tests pass
        except Exception as e:
            print(f"Test failed: {e}")
            return False # Return False if any test fails


    def run_test(self, test_case):
        self.driver.get("https://github.com/login")
        forgot_password_link = self.locate_element({"id": "forgot-password"})
        forgot_password_link.click()
        self.assertEqual(self.driver.current_url, "https://github.com/password_reset")
        print("Test passed: User redirected to password reset page.")


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestForgotPasswordNavigation))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if tests fail, 0 if pass