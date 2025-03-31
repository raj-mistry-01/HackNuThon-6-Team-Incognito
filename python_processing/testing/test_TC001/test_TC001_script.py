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
            # Check for error message in the URL (e.g., ?error=login_failure)
            if "error" in self.driver.current_url:
                return True

            # Check for specific error elements on the page
            error_element = self.driver.find_element(By.CSS_SELECTOR, ".flash-error") # Example error class
            if error_element:
                return True
            
            # Check for JavaScript errors in the browser console
            for entry in self.driver.get_log('browser'):
                if entry['level'] == 'SEVERE':  # Or other relevant log levels
                    return True
        except NoSuchElementException:
            pass  # No error element found
        return False


    def test_login_empty_credentials(self):
        self.driver.get("https://github.com/login")

        username_field = self.locate_element({"id": "login_field"})
        password_field = self.locate_element({"id": "password"})
        sign_in_button = self.locate_element({"css": ".js-sign-in-button"})

        username_field.clear()
        password_field.clear()
        sign_in_button.click()

        self.assertTrue(self.check_for_errors(), "Expected error messages not displayed.")


if __name__ == "__main__":
    test_result = unittest.main(exit=False).result
    failures = len(test_result.failures)
    errors = len(test_result.errors)

    if failures == 0 and errors == 0:
        print("Test Passed: True")
        exit(0)  # Exit code 0 for pass
    else:
        print("Test Passed: False")
        exit(1)  # Exit code 1 for failure