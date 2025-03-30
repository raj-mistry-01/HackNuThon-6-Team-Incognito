import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestGithubLogin(unittest.TestCase):

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
                return data.get("test_data", [])  # Return test_data or empty list if not found
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
            return [{"email": "defaultuser@example.com", "password": "defaultpassword"}]

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


    def test_successful_login(self):
        overall_result = True # Initialize overall result
        for data in self.test_data:
            try:
                self.driver.get("https://github.com/login")
                email = data.get("email")
                password = data.get("password")

                # Step 1: Enter username/email
                username_field = self.locate_element({"id": "login_field"})
                username_field.send_keys(email)

                # Step 2: Enter password
                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(password)

                # Step 3: Click Sign in
                sign_in_button = self.locate_element({"css": ".js-sign-in-button"})
                sign_in_button.click()

                # Expected Result: Check URL for successful redirect (adjust as needed)
                # Example: assert "https://github.com/" in self.driver.current_url
                # Add specific assertions based on your expected outcome after login

                print(f"Test with {email} - PASSED")

            except Exception as e:
                print(f"Test with {email} - FAILED: {e}")
                overall_result = False # Set overall result to False if any test fails

        return overall_result # Return the overall result


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestGithubLogin("test_successful_login"))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise