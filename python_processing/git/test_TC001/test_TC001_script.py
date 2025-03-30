import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

class TestGithubLogin(unittest.TestCase):

    def setUp(self):
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        self.driver = webdriver.Firefox(options=options)
        self.driver.get("https://github.com/login")

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
            test_data_list = [{"email": "defaultuser@example.com", "password": "defaultpassword"}]

        overall_result = True
        for test_data in test_data_list:
            try:
                email = test_data["email"]
                password = test_data["password"]

                # Step 1: Enter username/email
                username_field = self.locate_element({"id": "login_field", "css": "#login_field", "xpath": "//input[@id='login_field']"})
                username_field.send_keys(email)

                # Step 2: Enter password
                password_field = self.locate_element({"id": "password", "css": "#password", "xpath": "//input[@id='password']"})
                password_field.send_keys(password)

                # Step 3: Click Sign in
                sign_in_button = self.locate_element({"css": ".js-sign-in-button", "xpath": "//input[@value='Sign in']"})
                sign_in_button.click()

                # Assertion: Check if redirected (simple check for URL change -  replace with more robust check if needed)
                self.assertNotEqual(self.driver.current_url, "https://github.com/login", f"Login failed for {email}")
                print(f"Test passed for {email}")


            except Exception as e:
                print(f"Test failed for {email}: {e}")
                overall_result = False  # Set overall result to False if any test fails

        return overall_result # Return True if all tests pass, False otherwise


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestGithubLogin))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise