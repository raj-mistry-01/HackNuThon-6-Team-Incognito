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
                        return False, f"Console error: {log['message']}"

            # Check for URL error parameters (e.g., ?error=something)
            url = self.driver.current_url
            if "?error=" in url or "&error=" in url:
                return False, f"URL indicates error: {url}"

            # Check for specific error elements on the page
            try:
                error_element = self.driver.find_element(By.ID, "error_message_id") # Replace with actual error element selector if known
                return False, f"Error message displayed: {error_element.text}"
            except NoSuchElementException:
                pass # No error element found

            return True, ""  # No errors detected

        except Exception as e:
            return False, f"Error during error check: {e}"


    def test_login_long_email(self):
        try:
            with open("testcase.json", "r") as f:
                test_data_list = json.load(f).get("test_data", [])
        except FileNotFoundError:
            test_data_list = []

        if not test_data_list:
            test_data_list = [{"email": "extremelylongemail" * 20 + "@example.com", "password": "valid_password"}]

        for test_data in test_data_list:
            email = test_data.get("email", "extremelylongemail" * 20 + "@example.com")
            password = test_data.get("password", "valid_password")

            self.driver.get("https://github.com/login")

            try:
                email_field = self.locate_element({"id": "login_field"})
                email_field.send_keys(email)

                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(password)

                sign_in_button = self.locate_element({"css": "input[type='submit'][name='commit']"})
                sign_in_button.click()

                is_passed, error_message = self.check_for_errors()
                self.assertTrue(is_passed, error_message) # Check for any type of error


            except Exception as e:
                print(f"Test failed: {e}")
                return False # Explicitly return False on failure

        return True  # Explicitly return True on success


if __name__ == "__main__":
    test_result = TestLogin().test_login_long_email()
    print(f"Test Result: {test_result}")