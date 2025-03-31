import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

class TestLoginSQLInjection(unittest.TestCase):

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
            except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
                continue  # Try the next selector
        raise Exception(f"Could not locate element with selectors: {selectors}")
    
    def check_for_errors(self):
        try:
            # Check for console errors
            console_logs = self.driver.get_log('browser')
            for log in console_logs:
                if log['level'] == 'SEVERE':  # Or other relevant log levels
                    print(f"Console Error: {log['message']}")
                    return False

            # Check for URL-based errors (e.g., error parameters)
            current_url = self.driver.current_url
            if "error" in current_url.lower() or "exception" in current_url.lower(): # Customize as needed
                print(f"URL Error: {current_url}")
                return False

            # Check for specific error elements on the page
            try:
                error_element = self.driver.find_element(By.ID, "error_message_id") # Replace with actual error element selector if known
                print(f"Page Error: {error_element.text}")
                return False
            except NoSuchElementException:
                pass  # No error element found

        except Exception as e:
            print(f"Error during error check: {e}")
            return False  # Consider this a failure if error checking itself fails

        return True # No errors detected


    def test_login_sql_injection(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f).get("test_data", [])
        except FileNotFoundError:
            test_data = []

        if not test_data:
            test_data = [{"username": "test@example.com' or '1'='1' --", "password": "password123"}] # Default values

        for data in test_data:
            try:
                self.driver.get("https://github.com/login")

                username_field = self.locate_element({"id": "login_field"})
                username_field.clear()
                username_field.send_keys(data.get("username", "test@example.com' or '1'='1' --"))

                password_field = self.locate_element({"id": "password"})
                password_field.clear()
                password_field.send_keys(data.get("password", "password123"))

                sign_in_button = self.locate_element({"css": ".js-sign-in-button"})
                sign_in_button.click()

                if not self.check_for_errors():
                    self.test_passed = False

                # Assertion to check if login failed (as expected for SQL injection attempt)
                try:
                    error_message = self.locate_element({"css": ".flash-error"}, wait_time=5) # Adjust selector if needed
                    self.assertTrue("Incorrect username or password." in error_message.text, "Expected error message not found")
                except Exception:
                    self.fail("Login unexpectedly succeeded or a different error occurred.")


            except Exception as e:
                print(f"Test failed: {e}")
                self.test_passed = False

        print("Test Passed" if self.test_passed else "Test Failed")
        return self.test_passed



if __name__ == "__main__":
    result = unittest.main(exit=False).result
    if len(result.failures) + len(result.errors) == 0:
        exit(0)  # Exit code 0 for success
    else:
        exit(1)  # Exit code 1 for failure