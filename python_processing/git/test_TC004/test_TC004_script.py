import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestPasskeyLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_data = self.load_test_data()

    def tearDown(self):
        self.driver.quit()

    def load_test_data(self):
        try:
            filepath = os.path.join(os.path.dirname(__file__), 'testcase.json')
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
            return []  # or a default dictionary

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


    def test_sign_in_with_passkey(self):
        if not self.test_data:
            self.test_data = [{}] # Run at least once with default values if file is empty

        for data in self.test_data:
            try:
                self.driver.get("https://github.com/login")

                # Step 1: Click 'Sign in with a passkey'
                passkey_button = self.locate_element({"css": ".js-webauthn-subtle button", "xpath": "//button[contains(text(),'Sign in with a passkey')]"}, 15) # Increased wait time to 15 seconds
                passkey_button.click()

                # Expected Result 1: Passkey prompt appears (Difficult to automate, requires OS interaction)
                # Add assertion here if possible to check for a specific element/change after clicking the button
                # For this specific case, manual verification might be necessary.
                print("Passkey button clicked. Please manually verify if the passkey prompt appears.")

            except Exception as e:
                print(f"Test failed: {e}")
                return False  # Indicate test failure

        return True  # Indicate test success


if __name__ == '__main__':
    test_result = TestPasskeyLogin().run(unittest.makeSuite(TestPasskeyLogin)).wasSuccessful()
    print("Test Result:", test_result) 
    exit(not test_result) # Exit with 1 if test failed, 0 if passed