import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestForgotPassword(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_data = self.load_test_data()

    def tearDown(self):
        self.driver.quit()

    def load_test_data(self):
        try:
            with open("testcase.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
            return {}  # Return empty dict if file not found

    def locate_element(self, selectors, wait_time=10):
        wait = WebDriverWait(self.driver, wait_time)
        for selector_type, selector_value in selectors.items():
            if not selector_value:
                continue
            try:
                if selector_type == "id":
                    return wait.until(EC.presence_of_element_located((By.ID, selector_value)))
                elif selector_type == "css":
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_value)))
                elif selector_type == "xpath":
                    return wait.until(EC.presence_of_element_located((By.XPATH, selector_value)))
                elif selector_type == "name":
                    return wait.until(EC.presence_of_element_located((By.NAME, selector_value)))
            except Exception:
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def test_forgot_password(self):
        try:
            # Navigate to the login page
            self.driver.get("https://github.com/login")

            # Find and click the "Forgot password?" link
            forgot_password_link = self.locate_element(self.test_data.get("elements", [{"selectors": {"id": "forgot-password"}}])[0]["selectors"])
            forgot_password_link.click()

            # Assert that the URL has changed, indicating redirection
            self.assertIn("password_reset", self.driver.current_url) 
            print("Test Passed")
            return True

        except Exception as e:
            print(f"Test Failed: {e}")
            return False


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestForgotPassword("test_forgot_password"))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if tests fail, 0 if they pass