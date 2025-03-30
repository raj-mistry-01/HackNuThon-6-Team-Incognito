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
            except (NoSuchElementException, TimeoutException):
                continue  # Try the next selector
        raise Exception(f"Could not locate element with selectors: {selectors}")
    
    def check_for_errors(self):
        # Check for console errors
        try:
            console_logs = self.driver.get_log('browser')
            for log in console_logs:
                if log['level'] == 'SEVERE':  # Or other relevant log levels
                    print(f"Console Error: {log['message']}")
                    self.test_passed = False
                    return  # Stop checking if a severe error is found
        except Exception as e:
            print(f"Error checking console logs: {e}")
            self.test_passed = False
            return

        # Check for URL errors (e.g., error parameters)
        try:
            current_url = self.driver.current_url
            if "error" in current_url.lower():  # Or other error indicators
                print(f"URL Error: {current_url}")
                self.test_passed = False
                return
        except Exception as e:
            print(f"Error checking URL: {e}")
            self.test_passed = False
            return

        # Check for error elements on the page
        try:
            error_element = self.driver.find_element(By.ID, "error_div") # Replace with actual error element selector if known
            if error_element.is_displayed():
                print(f"Page Error: {error_element.text}")
                self.test_passed = False
                return
        except NoSuchElementException:
            pass # No error element found, which is expected in some cases
        except Exception as e:
            print(f"Error checking for error element: {e}")
            self.test_passed = False
            return


    def test_login_sql_injection(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f).get("test_data", [])
        except FileNotFoundError:
            test_data = []

        if not test_data:
            test_data = [{}]  # Run with default values if no test data

        for data in test_data:
            self.driver.get("https://github.com/login")

            # Step 1: Enter SQL injection string
            username_field = self.locate_element({"id": "login_field"})
            username_field.clear()
            username_field.send_keys("' OR '1'='1")


            # Step 2: Enter password (any value)
            password_field = self.locate_element({"id": "password"})
            password_field.clear()
            password_field.send_keys("dummy_password")

            # Step 3: Click Sign in
            sign_in_button = self.locate_element({"css": "input[type='submit']", "xpath": "//input[@value='Sign in']"})
            sign_in_button.click()
            
            self.check_for_errors()

            # Assertions (Generic login failure expected - adjust as needed based on actual behavior)
            try:
                # Example: Check if an error message is displayed (replace with actual selector)
                error_message = self.locate_element({"id": "js-flash-container .flash-error"}) # Example selector - replace with actual
                self.assertTrue(error_message.is_displayed(), "Login should have failed, but no error message was found.")
            except NoSuchElementException:
                self.test_passed = False # Or handle differently based on expected behavior
                print("Login failed, but no expected error message element was found.")
            except Exception as e:
                self.test_passed = False
                print(f"An unexpected error occurred during assertion: {e}")


        print("Test Passed" if self.test_passed else "Test Failed")
        return self.test_passed


if __name__ == "__main__":
    result = TestLoginSQLInjection().test_login_sql_injection()
    exit(not result) # Exit with 1 if test failed, 0 if passed