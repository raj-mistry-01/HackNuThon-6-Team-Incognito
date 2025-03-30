import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class TestLogin(unittest.TestCase):

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
                elif selector_type == "value":
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[value="{selector_value}"]')))

            except (NoSuchElementException, TimeoutException):
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def test_login_domainless_email(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "testcase.json"), "r") as f:
                test_data_list = json.load(f).get("test_data", [])
        except (FileNotFoundError, json.JSONDecodeError):
            test_data_list = [{"email": "test", "password": "password123"}]  # Default values

        overall_result = True
        for test_data in test_data_list:
            try:
                self.driver.get("https://github.com/login")

                email_field = self.locate_element({"id": "login_field"})
                email_field.send_keys(test_data["email"])

                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(test_data["password"])

                sign_in_button = self.locate_element({"type": "submit", "value": "Sign in"})
                sign_in_button.click()

                # Error Handling and Assertions
                try:
                    error_message = self.driver.find_element(By.CSS_SELECTOR, ".flash-error") # Generic error selector
                    print(f"Test with {test_data} - Passed (Error message displayed: {error_message.text})")
                    self.assertTrue(error_message.is_displayed()) # Check if error is displayed
                except NoSuchElementException:
                    print(f"Test with {test_data} - Failed (No error message displayed)")
                    overall_result = False
                    self.fail("No error message displayed")

                # Check for errors in console
                for entry in self.driver.get_log('browser'):
                    if entry['level'] == 'SEVERE':
                        print(f"Console error: {entry['message']}")
                        overall_result = False
                        self.fail(f"Console error: {entry['message']}")

            except Exception as e:
                print(f"Test with {test_data} - Failed: {e}")
                overall_result = False
                self.fail(str(e))

        return overall_result


if __name__ == "__main__":
    result = unittest.main(exit=False).result
    if len(result.failures) + len(result.errors) == 0:
        print("Overall Test Result: PASSED")
        exit(0)  # Exit code 0 for pass
    else:
        print("Overall Test Result: FAILED")
        exit(1)  # Exit code 1 for fail