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
            if console_logs:
                for log in console_logs:
                    if log['level'] == 'SEVERE':  # Or other relevant levels
                        print(f"Console Error: {log['message']}")
                        return False

            # Check for URL error parameters (e.g., ?error=something)
            if "?error=" in self.driver.current_url:
                print(f"URL Error: {self.driver.current_url}")
                return False

            # Check for specific error elements on the page
            try:
                error_element = self.driver.find_element(By.ID, "error_message_id") # Replace with actual error element selector if known
                print(f"Page Error: {error_element.text}")
                return False
            except NoSuchElementException:
                pass  # No specific error element found

        except Exception as e:
            print(f"Error during error check: {e}")
            return False  # Consider this a failure if error checking itself fails

        return True # No errors detected


    def test_login_with_email_spaces(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f).get("test_data", [])
        except FileNotFoundError:
            test_data = []

        if not test_data:
            test_data = [{"email": "test user@example.com", "password": "password123"}] # Default test data


        for data in test_data:
            try:
                self.driver.get("https://github.com/login")

                email_field = self.locate_element({"id": "login_field"})
                email_field.send_keys(data["email"])

                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(data["password"])

                sign_in_button = self.locate_element({"css": "input[type='submit']", "xpath": "//input[@value='Sign in']"})
                sign_in_button.click()

                if self.check_for_errors():  # Check for various error indicators
                    print("Test Passed for data:", data)
                    return True # Test passed if no errors found
                else:
                    print("Test Failed for data:", data)
                    return False # Test failed if errors found

            except Exception as e:
                print(f"Test failed due to an exception: {e}")
                return False


if __name__ == "__main__":
    test_result = TestLoginWithEmailSpaces().test_login_with_email_spaces()
    print(f"Overall Test Result: {'Pass' if test_result else 'Fail'}")