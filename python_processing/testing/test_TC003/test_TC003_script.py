import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

class TestLoginWithEmailSpaces(unittest.TestCase):

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


    def test_login_with_email_spaces(self):
        try:
            with open("testcase.json", "r") as f:
                test_data_list = json.load(f).get("test_data", [])
        except (FileNotFoundError, json.JSONDecodeError):
            test_data_list = []  # Use default values if file not found or invalid

        if not test_data_list:
            test_data_list = [{}] # Run at least once with default values

        for test_data in test_data_list:
            try:
                self.driver.get("https://github.com/login")

                email_with_spaces = test_data.get("email", "test user@example.com")
                password = test_data.get("password", "password123")

                # Step 1: Enter email with spaces
                email_field = self.locate_element({"id": "login_field"})
                email_field.send_keys(email_with_spaces)

                # Step 2: Enter password
                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(password)

                # Step 3: Click Sign in
                sign_in_button = self.locate_element({"css": "input[type='submit'][name='commit']"})
                sign_in_button.click()


                # Assertions (Check for error message)
                try:
                    # Check for error in the URL (some sites do this)
                    self.assertNotIn("error", self.driver.current_url.lower(), "Error found in URL")

                    # Check for a specific error element (adapt as needed)
                    error_element = self.locate_element({"id": "js-flash-container .flash-error"}, wait_time=5) # Example
                    self.assertTrue(error_element.is_displayed(), "Error message not displayed")

                except (NoSuchElementException, TimeoutException, AssertionError) as e:
                    # Check for JavaScript errors in the console
                    for log_entry in self.driver.get_log('browser'):
                        if log_entry['level'] == 'SEVERE':
                            print(f"JavaScript error: {log_entry['message']}")
                            self.test_passed = False
                            break  # Stop checking after the first severe error
                    if self.test_passed: # If no JS errors, re-raise the original exception
                        raise e

            except Exception as e:
                print(f"Test failed: {e}")
                self.test_passed = False

        return self.test_passed


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestLoginWithEmailSpaces))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if tests fail, 0 if they pass