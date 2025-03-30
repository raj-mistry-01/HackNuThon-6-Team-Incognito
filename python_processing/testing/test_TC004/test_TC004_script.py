import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

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
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def check_for_errors(self):
        try:
            # Check for alert messages
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()  # Or alert.dismiss() depending on the scenario
            print(f"Alert detected: {alert_text}")
            return True # Found an error

        except Exception:
            pass # No alert present


        try:
            # Check for error messages in the URL (e.g., error parameters)
            error_in_url = "error" in self.driver.current_url.lower()
            if error_in_url:
                print("Error parameter found in URL")
                return True # Found an error
        except Exception:
            pass

        try:
            # Check for specific error divs or elements on the page
            error_div = self.driver.find_element(By.ID, "error_div") # Replace with actual error div ID
            error_message = error_div.text
            print(f"Error message found on page: {error_message}")
            return True # Found an error
        except NoSuchElementException:
            pass # No error div found

        try:
            # Check for console errors
            for entry in self.driver.get_log('browser'):
                if entry['level'] == 'SEVERE':  # Or other relevant log levels
                    print(f"Console error: {entry['message']}")
                    return True # Found an error
        except Exception:
            pass

        return False # No errors detected



    def test_login_sql_injection(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f).get("test_data", [])
        except FileNotFoundError:
            test_data = []

        if not test_data:
            test_data = [{"username": "'admin' or '1=1--", "password": "password123"}] # Default values

        for data in test_data:
            username = data.get("username", "'admin' or '1=1--")
            password = data.get("password", "password123")

            self.driver.get("https://github.com/login")

            try:
                username_field = self.locate_element({"id": "login_field"})
                username_field.send_keys(username)

                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(password)

                sign_in_button = self.locate_element({"css": "input[type='submit']", "xpath": "//input[@value='Sign in']"})
                sign_in_button.click()

                # Assertions and Error Checks
                if self.check_for_errors():
                    print("Test Passed: SQL Injection attempt blocked.")
                else:
                    print("Test Failed: SQL Injection attempt was not blocked.")
                    self.test_passed = False

                # Add more assertions based on specific error messages if needed

            except Exception as e:
                print(f"Test Failed: An unexpected error occurred: {e}")
                self.test_passed = False


        return self.test_passed



if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestLoginSQLInjection("test_login_sql_injection"))
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(test_suite)
    exit_code = 0 if test_result.wasSuccessful() else 1
    exit(exit_code)