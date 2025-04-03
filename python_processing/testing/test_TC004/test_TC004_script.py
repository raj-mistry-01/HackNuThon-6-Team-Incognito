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
        self.driver.get("https://github.com/login")

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
        # Check for console errors
        try:
            console_logs = self.driver.get_log('browser')
            for log in console_logs:
                if log['level'] == 'SEVERE':  # Or other relevant levels
                    return False, f"Console error: {log['message']}"
        except Exception as e:
            return False, f"Error checking console logs: {e}"

        # Check for URL-based errors (e.g., error parameters)
        current_url = self.driver.current_url
        if "error" in current_url.lower() or "exception" in current_url.lower():  # Customize as needed
            return False, f"URL indicates an error: {current_url}"

        # Check for error elements on the page (divs, alerts, etc.)
        try:
            error_element = self.driver.find_element(By.CSS_SELECTOR, ".flash-error") # Example selector, adapt as needed
            return False, f"Error element found on page: {error_element.text}"
        except NoSuchElementException:
            pass  # No error element found

        return True, "" # No errors detected


    def test_login_sql_injection(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f).get("test_data", [])
        except FileNotFoundError:
            test_data = []

        if not test_data:
            test_data = [{}]  # Run with default values if no test data

        for data in test_data:
            try:
                username_field = self.locate_element({"id": "login_field"})
                username_field.clear()
                username_field.send_keys("' OR '1'='1")

                password_field = self.locate_element({"id": "password"})
                password_field.clear()
                password_field.send_keys("dummy_password")  # Any password

                sign_in_button = self.locate_element({"css": "input[type='submit'][name='commit']"})
                sign_in_button.click()


                is_pass, error_message = self.check_for_errors()
                if not is_pass:
                    print(f"Test failed: {error_message}")
                    self.fail(error_message)  # Fail the test if errors are found
                else:
                    # Assertions for successful negative login (no SQL injection success)
                    # Example: Check that the user is NOT redirected to a dashboard/profile page
                    self.assertIn("login", self.driver.current_url.lower(), "Login should have failed, but seems to have succeeded.")
                    print("Test passed: SQL Injection attempt thwarted.")


            except Exception as e:
                print(f"Test failed: {e}")
                self.fail(str(e))
                return False # Explicitly return False on failure

        return True # Return True if all tests pass



if __name__ == "__main__":
    result = unittest.main(exit=False).result
    if len(result.failures) == 0 and len(result.errors) == 0:
        exit(0) # Exit code 0 for success
    else:
        exit(1) # Exit code 1 for failure