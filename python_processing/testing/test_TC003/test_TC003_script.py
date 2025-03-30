import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

class TestLoginWithSpacesInUsername(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_data = []
        try:
            with open("testcase.json", "r") as f:
                test_case = json.load(f)
                self.test_data = test_case.get("test_data", [])
        except FileNotFoundError:
            print("testcase.json not found, using default values.")

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
            except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
                continue  # Try the next selector
        raise Exception(f"Could not locate element with selectors: {selectors}")
    
    def check_for_errors(self):
        try:
            # Check for console errors
            console_logs = self.driver.get_log('browser')
            if console_logs:
                for log in console_logs:
                    if log['level'] == 'SEVERE':  # Or other relevant levels
                        return False, f"Console error: {log['message']}"

            # Check for URL errors (e.g., error parameters)
            url = self.driver.current_url
            if "error" in url.lower(): # Or any specific error pattern
                return False, f"URL indicates error: {url}"

            # Check for error elements on the page
            try:
                error_element = self.driver.find_element(By.ID, "error_message_id") # Replace with actual error element selector if known
                # or
                error_element = self.driver.find_element(By.CSS_SELECTOR, ".error-message") # Example CSS selector
                return False, f"Error element found: {error_element.text}"
            except NoSuchElementException:
                pass # No error element found

            return True, "" # No errors detected

        except Exception as e:
            return False, f"An unexpected error occurred during error checking: {e}"



    def test_login_with_spaces(self):
        if not self.test_data:
            self.test_data = [{"username": "test user", "password": "password123"}] # Default test data

        for data in self.test_data:
            username = data.get("username", "test user")
            password = data.get("password", "password123")

            self.driver.get("https://github.com/login")

            try:
                username_field = self.locate_element({"id": "login_field"})
                username_field.send_keys(username)

                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(password)

                sign_in_button = self.locate_element({"css": "input[type='submit']", "xpath": "//input[@value='Sign in']"})
                sign_in_button.click()

                is_passed, error_message = self.check_for_errors()
                self.assertTrue(is_passed, error_message) # Check for various error types

                # Additional assertions to check if login failed as expected
                # Example: Check if still on the login page or an error message is displayed
                self.assertIn("login", self.driver.current_url.lower(), "Login should have failed, but redirected away from login page.")


            except Exception as e:
                print(f"Test failed: {e}")
                self.fail(str(e)) # Fail the test case if any exception occurs
            


if __name__ == "__main__":
    test_result = unittest.main(exit=False).result
    failures = len(test_result.failures)
    errors = len(test_result.errors)
    print(f"Tests run: {test_result.testsRun}, Failures: {failures}, Errors: {errors}")
    exit(failures + errors) # Exit with non-zero status if there are failures or errors