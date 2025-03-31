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
                        print(f"Console Error: {log}")
                        return False

            # Check for error in URL (e.g., after a redirect)
            if "error" in self.driver.current_url.lower():  # Adjust as needed
                print(f"Error in URL: {self.driver.current_url}")
                return False

            # Check for a generic error div (customize as needed)
            try:
                error_div = self.driver.find_element(By.ID, "error-message") # Or CSS selector, XPath
                print(f"Error message on page: {error_div.text}")
                return False
            except NoSuchElementException:
                pass  # No error div found

        except Exception as e:
            print(f"An unexpected error occurred during error checking: {e}")
            return False  # Consider this a failure

        return True # No errors detected


    def test_login_long_email(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f).get("test_data", [])
        except FileNotFoundError:
            test_data = []

        if not test_data:
            test_data = [{"email": "extremelylongemail" * 15 + "@example.com", "password": "password123"}]

        for data in test_data:
            try:
                self.driver.get("https://github.com/login")

                email_field = self.locate_element({"id": "login_field"})
                email_field.send_keys(data["email"])

                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(data["password"])

                sign_in_button = self.locate_element({"css": ".js-sign-in-button"})
                sign_in_button.click()

                if not self.check_for_errors():
                    return False # Test failed due to detected errors

                # Add assertions based on your expected behavior (e.g., error message, truncated email)
                # Example:
                # error_message = self.locate_element({"id": "error-message"}) # Replace with actual error element selector
                # self.assertTrue("Email too long" in error_message.text)

            except Exception as e:
                print(f"Test failed: {e}")
                return False

        return True  # All tests passed


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestLogin))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if tests fail, 0 if they pass