import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestFailedLogin(unittest.TestCase):

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
            print("testcase.json not found, using default test data.")
            return [{"email": "invaliduser@example.com", "password": "wrongpassword"}]  # Default data

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
            except Exception:
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def test_failed_login(self):
        overall_result = True  # Initialize overall result
        for data in self.test_data:
            try:
                self.driver.get("https://github.com/login")
                email = data.get("email", "invaliduser@example.com")  # Get email from data or use default
                password = data.get("password", "wrongpassword")  # Get password from data or use default

                # Step 1: Enter invalid username/email
                username_field = self.locate_element({"id": "login_field"})
                username_field.send_keys(email)

                # Step 2: Enter invalid password
                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(password)

                # Step 3: Click the 'Sign in' button
                sign_in_button = self.locate_element({"css": "input[type='submit'][name='commit']", "xpath": "//input[@value='Sign in']"})
                sign_in_button.click()

                # Expected Result 1: Verify error message
                # Assuming the error message appears near the password field, adjust selector if needed
                error_message = self.locate_element({"id": "js-flash-container"})
                self.assertTrue(error_message.is_displayed(), "Error message not displayed")
                print(f"Test passed for data: {data}")

            except Exception as e:
                print(f"Test failed for data: {data}. Error: {e}")
                overall_result = False # Set overall result to False if any test fails

        return overall_result # Return the overall result


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestFailedLogin))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise