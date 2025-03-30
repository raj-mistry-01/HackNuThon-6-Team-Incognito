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
        self.test_data = []
        try:
            with open("testcase.json", "r") as f:
                testcase = json.load(f)
                self.test_data = testcase.get("test_data", [])
        except FileNotFoundError:
            print("testcase.json not found, using default test data.")
        if not self.test_data:
            self.test_data = [{"email": "test @example.com", "password": "password123"}]  # Default data

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
                elif selector_type == "type":
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[type="{selector_value}"]')))
                elif selector_type == "value": # Added to handle value selector
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[value="{selector_value}"]')))
            except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
                continue  # Try the next selector
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def test_login_with_email_spaces(self):
        overall_result = True
        for data in self.test_data:
            try:
                self.driver.get("https://github.com/login")
                email_field = self.locate_element({"id": "login_field"})
                password_field = self.locate_element({"id": "password"})
                sign_in_button = self.locate_element({"type": "submit", "value": "Sign in"})

                email_field.send_keys(data["email"])
                password_field.send_keys(data["password"])
                sign_in_button.click()

                # Assertions - Enhanced error handling
                try:
                    error_message = self.driver.find_element(By.CSS_SELECTOR, ".flash-error").text
                    self.assertIn("Incorrect username or password.", error_message, "Expected error message not found") # Adjust error message as needed
                except NoSuchElementException:
                    url = self.driver.current_url
                    self.assertEqual(url, "https://github.com/login", "Unexpected URL after login attempt")
                    print("No error message displayed, but URL indicates login failure.")
                    overall_result = False # Set overall result to False if any test data fails

            except Exception as e:
                print(f"Test failed for data: {data} with error: {e}")
                overall_result = False # Set overall result to False if any test data fails
        return overall_result # Return overall result


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestLoginWithEmailSpaces))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise