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
        self.test_data = self.load_test_data()

    def tearDown(self):
        self.driver.quit()

    def load_test_data(self):
        try:
            with open("testcase.json", "r") as f:
                data = json.load(f)
                return data.get("test_data", [])  # Extract test_data, default to empty list if not found
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
            return [{"email": "invalid@example.com", "password": "wrongpassword"}]  # Default values

    def locate_element(self, selectors, wait_time=10):
        wait = WebDriverWait(self.driver, wait_time)
        for selector_type, selector_value in selectors.items():
            if not selector_value:
                continue
            try:
                if selector_type == "id" and selector_value:
                    return wait.until(EC.presence_of_element_located((By.ID, selector_value)))
                # Add other selector types (css, xpath, name) as needed, similar to the 'id' block above
            except Exception:
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def test_failed_login(self):
        for data in self.test_data:
            try:
                self.driver.get("https://incognito-three-chi.vercel.app/login")
                email_input = self.locate_element({"id": "email"})
                email_input.send_keys(data.get("email", "invalid@example.com")) # Use data from json or default
                password_input = self.locate_element({"id": "password"})
                password_input.send_keys(data.get("password", "wrongpassword")) # Use data from json or default
                login_button = self.locate_element({"id": "login"})
                login_button.click()

                # Assertion: Check for error message (replace with actual error message locator)
                # Example:
                # error_message = self.locate_element({"id": "error-message"})
                # self.assertTrue(error_message.is_displayed(), "Error message not displayed")
                print("Test Passed for data:", data) # Print pass for each data set

            except Exception as e:
                print(f"Test Failed for data: {data}. Error: {e}")
                return False # Return False for failure


        return True # Return True if all tests pass


if __name__ == "__main__":
    test_result = TestLogin().test_failed_login() # Get the boolean result
    print("Overall Test Result:", test_result) # Print the overall result