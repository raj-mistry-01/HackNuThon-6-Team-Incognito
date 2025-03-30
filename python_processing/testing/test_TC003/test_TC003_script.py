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
                elif selector_type == "type": # Added for 'type' selector
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[type="{selector_value}"]')))
                elif selector_type == "value": # Added for 'value' selector
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[value="{selector_value}"]')))

            except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
                continue  # Try the next selector
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def check_for_errors(self):
        try:
            # Check for console errors
            console_logs = self.driver.get_log('browser')
            if console_logs:
                print("Console Errors Found:")
                for log in console_logs:
                    print(log)
                return False

            # Check for URL error parameters (e.g., ?error=something)
            if "?error=" in self.driver.current_url:
                print(f"Error in URL: {self.driver.current_url}")
                return False

            # Check for specific error elements on the page (adapt as needed)
            try:
                error_element = self.driver.find_element(By.ID, "error_message") # Replace with actual error element selector
                print(f"Error element found: {error_element.text}")
                return False
            except NoSuchElementException:
                pass # No error element found

        except Exception as e:
            print(f"An unexpected error occurred during error checking: {e}")
            return False  # Consider this a failure

        return True # No errors detected


    def test_login_long_email(self):
        try:
            with open("testcase.json", "r") as f:
                test_data_list = json.load(f).get("test_data", [])
        except (FileNotFoundError, json.JSONDecodeError):
            test_data_list = [{"email": "default_long_email@example.com", "password": "default_password"}]

        overall_result = True # Initialize overall result

        for test_data in test_data_list:
            try:
                self.driver.get("https://github.com/login")

                email = test_data.get("email")
                password = test_data.get("password")

                self.locate_element({"id": "login_field"}).send_keys(email)
                self.locate_element({"id": "password"}).send_keys(password)
                self.locate_element({"type": "submit", "value": "Sign in"}).click()

                if not self.check_for_errors():
                    overall_result = False # Update overall result if a test case fails
                    continue # Proceed to the next test data set

                # Add assertions for expected results (e.g., error message or truncated email)
                # Example:
                # error_message = self.locate_element({"id": "error_message"}).text
                # self.assertIn("Email too long", error_message)

            except Exception as e:
                print(f"Test case failed: {e}")
                overall_result = False # Update overall result if a test case fails

        print("Overall Test Result:", overall_result)
        return overall_result # Return the overall result


if __name__ == "__main__":
    result = TestLogin().test_login_long_email()
    if result:
        exit(0)  # Exit code 0 for success
    else:
        exit(1)  # Exit code 1 for failure