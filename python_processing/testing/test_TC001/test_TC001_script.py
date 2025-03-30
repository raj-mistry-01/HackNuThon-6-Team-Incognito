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
            except (NoSuchElementException, TimeoutException):
                continue  # Try the next selector
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def test_login_empty_credentials(self):
        if not self.test_data:
            self.test_data = [{}] # Run at least once with default values

        for data in self.test_data:
            try:
                self.driver.get("https://github.com/login")

                # Step 1 & 2: Leave fields empty (no action needed as they are empty by default)
                username_field = self.locate_element({"id": "login_field"})
                password_field = self.locate_element({"id": "password"})

                # Step 3: Click Sign in
                sign_in_button = self.locate_element({"css": "input[type='submit']", "xpath": "//input[@value='Sign in']"})
                sign_in_button.click()

                # Assertions
                error_messages = self.driver.find_elements(By.CSS_SELECTOR, ".flash-error")  # More generic error selector
                self.assertTrue(any("username or email address is required" in msg.text for msg in error_messages), "Username error not found")
                self.assertTrue(any("password is required" in msg.text for msg in error_messages), "Password error not found")
                print("Test passed for data:", data)
                return True # Test passed

            except Exception as e:
                print(f"Test failed for data: {data}. Error: {e}")
                # Check for JavaScript errors or other unexpected behavior
                for entry in self.driver.get_log('browser'):
                    print(f"Browser log: {entry}")
                return False # Test failed



if __name__ == "__main__":
    test_result = unittest.main(exit=False).result
    if len(test_result.failures) == 0 and len(test_result.errors) == 0:
        exit(0)  # Exit with 0 for success
    else:
        exit(1)  # Exit with 1 for failure