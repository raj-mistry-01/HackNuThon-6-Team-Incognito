import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

class TestLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_passed = True

    def tearDown(self):
        self.driver.quit()

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
            except (NoSuchElementException, TimeoutException):
                continue  # Try the next selector
        raise Exception(f"Could not locate element with selectors: {selectors}")

    def check_for_errors(self):
        try:
            # Check for console errors
            console_logs = self.driver.get_log('browser')
            if console_logs:
                for log in console_logs:
                    if log['level'] == 'SEVERE':  # Or other relevant levels
                        print(f"Console error: {log}")
                        return False

            # Check for error in URL (e.g., after a redirect)
            if "error" in self.driver.current_url.lower():  # Adjust as needed
                print(f"Error in URL: {self.driver.current_url}")
                return False

            # Check for specific error elements on the page
            try:
                error_element = self.driver.find_element(By.ID, "error_message") # Replace with actual error element selector
                print(f"Error message on page: {error_element.text}")
                return False
            except NoSuchElementException:
                pass # No error element found

            return True # No errors detected

        except Exception as e:
            print(f"Error during error check: {e}")
            return False


    def test_login_long_username(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f).get("test_data", [])
        except (FileNotFoundError, json.JSONDecodeError):
            test_data = []

        if not test_data:
            test_data = [{"username": "a" * 256, "password": "valid_password"}] # Default test data

        for data in test_data:
            try:
                self.driver.get("https://github.com/login")

                username_field = self.locate_element({"id": "login_field"})
                username_field.send_keys(data["username"])

                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(data["password"])

                sign_in_button = self.locate_element({"css": "input[type='submit']", "xpath": "//input[@value='Sign in']"})
                sign_in_button.click()

                if not self.check_for_errors():
                    print("Test passed: Login failed as expected for long username.")
                else:
                    print("Test failed: Login succeeded unexpectedly with long username.")
                    self.test_passed = False

            except Exception as e:
                print(f"Test failed with exception: {e}")
                self.test_passed = False

        return self.test_passed


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestLogin("test_login_long_username"))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise