import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

class TestGithubLogin(unittest.TestCase):

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
                        print(f"Console error: {log['message']}")
                        self.test_passed = False
                        return  # Stop checking after the first severe error

            # Check for URL errors (e.g., error parameters)
            url = self.driver.current_url
            if "error" in url.lower():  # Or other error indicators
                print(f"URL indicates an error: {url}")
                self.test_passed = False
                return

            # Check for error elements on the page
            try:
                error_element = self.driver.find_element(By.CSS_SELECTOR, ".flash-error") # Example error div
                print(f"Error element found on page: {error_element.text}")
                self.test_passed = False
                return
            except NoSuchElementException:
                pass # No error element found

        except Exception as e:
            print(f"Error during error checking: {e}")
            self.test_passed = False


    def test_login_empty_credentials(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            test_data = {}  # Use default values if file not found or invalid

        self.driver.get("https://github.com/login")

        # Locate elements using the provided selectors
        username_field = self.locate_element({"id": "login_field"})
        password_field = self.locate_element({"id": "password"})
        sign_in_button = self.locate_element({"css": "input[type='submit']", "xpath": "//input[@value='Sign in']"})

        username_field.clear()
        password_field.clear()
        sign_in_button.click()

        self.check_for_errors() # Check for all types of errors

        # Assertions (example - adapt as needed based on actual error messages)
        try:
            username_error = self.locate_element({"id": "login_field-error"})
            self.assertTrue(username_error.is_displayed(), "Username error message not displayed")
        except:
            self.test_passed = False
            print("Username error not found")

        try:
            password_error = self.locate_element({"id": "password-error"})
            self.assertTrue(password_error.is_displayed(), "Password error message not displayed")
        except:
            self.test_passed = False
            print("Password error not found")

        print("Test Passed" if self.test_passed else "Test Failed")
        return self.test_passed



if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestGithubLogin("test_login_empty_credentials"))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if tests fail, 0 if they pass