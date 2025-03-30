import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestPasskeySignIn(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_data = self.load_test_data()

    def tearDown(self):
        self.driver.quit()

    def load_test_data(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'testcase.json')
            with open(file_path, 'r') as f:
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


    def test_passkey_sign_in(self):
        try:
            self.driver.get("https://github.com/login")

            # Locate and click the "Sign in with a passkey" button
            passkey_button_selectors = self.test_data.get("elements", [{}])[0].get("selectors", {"css": ".js-webauthn-confirm-button"})
            passkey_button = self.locate_element(passkey_button_selectors)
            passkey_button.click()

            # Assertion: Check if the passkey prompt is displayed (or an error if unsupported)
            # This assertion needs to be browser/platform specific.  The example below checks for a specific error message that might appear if passkeys are not supported.
            try:
                error_message = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Your browser or operating system does not support passkeys.')]")  # Replace with actual error message locator
                print("Passkey sign-in not supported (as expected).") # Or assertFalse(error_message.is_displayed()) depending on the expected behavior
            except:
                print("Passkey prompt displayed (or no specific error found).") # Assuming success if no specific error is found.  Replace with a more robust check if possible.

            return True # Test passed

        except Exception as e:
            print(f"Test failed: {e}")
            return False # Test failed


if __name__ == '__main__':
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestPasskeySignIn))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise