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
            except (NoSuchElementException, TimeoutException):
                continue  # Try the next selector
        raise Exception(f"Could not locate element with selectors: {selectors}")
    
    def check_for_errors(self):
        try:
            # Check for console errors
            console_logs = self.driver.get_log('browser')
            if console_logs:
                for log in console_logs:
                    if log['level'] == 'SEVERE':  # Or other relevant levels
                        print(f"Console Error: {log}")
                        return False

            # Check for URL errors (e.g., specific parameters indicating errors)
            current_url = self.driver.current_url
            if "error" in current_url.lower() or "exception" in current_url.lower():  # Customize as needed
                print(f"URL Error: {current_url}")
                return False

            # Check for error elements on the page
            try:
                error_element = self.driver.find_element(By.CSS_SELECTOR, ".flash-error") # Example error div selector
                print(f"Page Error: {error_element.text}")
                return False
            except NoSuchElementException:
                pass  # No error element found

            return True  # No errors detected

        except Exception as e:
            print(f"Error during error checking: {e}")
            return False


    def test_login(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            test_data = {}  # Use default values if file is missing or empty

        website_url = test_data.get("website_url", "https://github.com/login")
        elements = test_data.get("elements", [])

        self.driver.get(website_url)

        try:
            # Perform login steps
            username_field = self.locate_element(elements[0]["selectors"])
            username_field.clear()  # Ensure the field is empty

            password_field = self.locate_element(elements[1]["selectors"])
            password_field.clear()  # Ensure the field is empty

            sign_in_button = self.locate_element(elements[2]["selectors"])
            sign_in_button.click()

            # Assertions
            self.assertFalse(self.check_for_errors(), "Errors detected during login.")

        except Exception as e:
            print(f"Test failed: {e}")
            return False  # Indicate test failure

        return True  # Indicate test success


if __name__ == "__main__":
    test_result = TestLogin().test_login()
    print(f"Test Result: {'PASS' if test_result else 'FAIL'}")