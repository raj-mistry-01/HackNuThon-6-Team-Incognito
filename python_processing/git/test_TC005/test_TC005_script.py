import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestPasskeySignInButton(unittest.TestCase):

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

    def test_passkey_sign_in_button_display(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "testcase.json"), "r") as f:
                test_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            test_data = {}  # Use default values if file not found or empty

        url = "https://github.com/login"  # Default URL

        self.driver.get(url)

        try:
            passkey_button = self.locate_element({"css": ".js-webauthn-confirm-button"})
            self.assertTrue(passkey_button.is_displayed(), "Passkey sign in button is not displayed.")
            print("Test Passed: Passkey sign in button is displayed.")
            return True
        except Exception as e:
            print(f"Test Failed: {e}")
            return False


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestPasskeySignInButton("test_passkey_sign_in_button_display"))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if test failed, 0 if passed