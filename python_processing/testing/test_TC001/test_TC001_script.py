import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

class TestGithubLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.get("https://github.com/login")

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
                elif selector_type == "type": # Added for 'type' selector
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[type="{selector_value}"]')))
                elif selector_type == "value": # Added for 'value' selector
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[value="{selector_value}"]')))

            except (StaleElementReferenceException, TimeoutException, NoSuchElementException):
                continue  # Try the next selector
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def test_empty_login(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            test_data = {}  # Use default values if file not found or invalid

        # Extract elements from test data or use defaults
        username_selectors = test_data.get("elements", [{}])[0].get("selectors", {"id": "login_field"})
        password_selectors = test_data.get("elements", [{}])[1].get("selectors", {"id": "password"})
        signin_selectors = test_data.get("elements", [{}])[2].get("selectors", {"type": "submit", "value": "Sign in"})


        try:
            # Perform test steps
            username_field = self.locate_element(username_selectors)
            password_field = self.locate_element(password_selectors)
            signin_button = self.locate_element(signin_selectors)

            username_field.clear()
            password_field.clear()
            signin_button.click()

            # Assertions (check for error messages)
            self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, "#js-flash-container .flash-error").is_displayed(), "Login error message not displayed")

            print("Test passed")
            return True

        except Exception as e:
            print(f"Test failed: {e}")
            return False


if __name__ == "__main__":
    test_result = TestGithubLogin().test_empty_login()
    print(f"Overall test result: {'Pass' if test_result else 'Fail'}")