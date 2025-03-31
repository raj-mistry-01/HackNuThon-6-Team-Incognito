import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

class TestLoginWithEmailSpace(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_passed = False

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
            # Check for error message element (adapt selector as needed)
            error_element = self.driver.find_element(By.CSS_SELECTOR, ".flash-error")
            return error_element.text
        except NoSuchElementException:
            pass  # No error element found

        try:
            # Check URL for error parameters
            if "error" in self.driver.current_url:
                return "Error in URL"
        except Exception as e:
            print(f"Error checking URL: {e}")

        try:
            # Check console logs for errors
            for entry in self.driver.get_log('browser'):
                if entry['level'] == 'SEVERE':
                    return entry['message']
        except Exception as e:
            print(f"Error checking console logs: {e}")
        
        return None  # No errors detected


    def test_login_with_email_space(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f).get("test_data", [])  # Get test data or empty list
        except FileNotFoundError:
            test_data = []

        if not test_data:
            test_data = [{}]  # Default data if file is empty or not found

        for data in test_data:
            try:
                self.driver.get("https://github.com/login")

                # Use data from testcase.json or default values
                username = data.get("username", "test @example.com")
                password = data.get("password", "password123")


                username_field = self.locate_element({"id": "login_field"})
                username_field.send_keys(username)

                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(password)

                sign_in_button = self.locate_element({"css": ".js-sign-in-button"})
                sign_in_button.click()

                error_message = self.check_for_errors()

                self.assertTrue(error_message, "No error message detected") # Check for any type of error
                print("Test Passed")
                self.test_passed = True

            except Exception as e:
                print(f"Test Failed: {e}")
                self.test_passed = False
            finally:
                # Ensure this is set for each iteration
                self.driver.delete_all_cookies()

        return self.test_passed


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestLoginWithEmailSpace("test_login_with_email_space"))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful())  # Exit with 1 if tests fail, 0 if they pass