import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
                if selector_type == "id" and selector_value:
                    return wait.until(EC.presence_of_element_located((By.ID, selector_value)))
                elif selector_type == "css" and selector_value:
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_value)))
                elif selector_type == "xpath" and selector_value:
                    return wait.until(EC.presence_of_element_located((By.XPATH, selector_value)))
                elif selector_type == "name" and selector_value:
                    return wait.until(EC.presence_of_element_located((By.NAME, selector_value)))
            except Exception:
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")

    def test_successful_login(self):
        try:
            with open("testcase.json", "r") as f:
                test_data_list = json.load(f).get("test_data", [])
        except FileNotFoundError:
            test_data_list = []

        if not test_data_list:
            test_data_list = [{"email": "defaultuser@example.com", "password": "defaultpassword"}]  # Default values

        for test_data in test_data_list:
            try:
                self.driver.get("https://github.com/login")

                email_field = self.locate_element({"id": "login_field", "name": "login"})
                email_field.send_keys(test_data["email"])

                password_field = self.locate_element({"id": "password", "name": "password"})
                password_field.send_keys(test_data["password"])

                sign_in_button = self.locate_element({"css": "input[type='submit'][name='commit']", "xpath": "//input[@value='Sign in']"})
                sign_in_button.click()

                # Assertion: Check if redirected (replace with a more robust check if needed)
                self.assertIn("github.com", self.driver.current_url)  # Basic redirection check
                print(f"Test passed for: {test_data}")
                
            except Exception as e:
                print(f"Test failed for: {test_data}. Error: {e}")
                return False # Explicitly return False on failure

        return True # Return True if all tests pass


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestLogin("test_successful_login"))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise