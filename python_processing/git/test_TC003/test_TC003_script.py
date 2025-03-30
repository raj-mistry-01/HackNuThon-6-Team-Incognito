import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestForgotPassword(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_data = self.load_test_data()

    def tearDown(self):
        self.driver.quit()

    def load_test_data(self):
        try:
            with open("testcase.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
            return {}  # Return empty dict for default behavior

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


    def test_forgot_password(self):
        try:
            # Load test data if available, otherwise use default URL
            url = self.test_data.get("website_url", "https://github.com/login")
            self.driver.get(url)

            # Locate and click the "Forgot password?" link
            forgot_password_link = self.locate_element({"id": "forgot-password"})
            forgot_password_link.click()

            # Assert that the URL has changed, indicating redirection
            self.assertNotEqual(url, self.driver.current_url, "URL did not change after clicking 'Forgot password?'")
            print("Test passed.")
            return True

        except Exception as e:
            print(f"Test failed: {e}")
            return False


if __name__ == "__main__":
    test_result = TestForgotPassword().test_forgot_password()
    if test_result:
        exit(0)  # Exit code 0 for pass
    else:
        exit(1)  # Exit code 1 (or any non-zero) for fail