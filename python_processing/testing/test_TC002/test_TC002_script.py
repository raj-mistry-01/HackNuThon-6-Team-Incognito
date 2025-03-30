import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class TestLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_data = []
        try:
            with open("testcase.json", "r") as f:
                test_case = json.load(f)
                self.test_data = test_case.get("test_data", [])
        except FileNotFoundError:
            print("testcase.json not found, using default values.")

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
            except Exception as e:
                print(f"Error locating element: {e}")
                continue  # Try the next selector
        raise NoSuchElementException(f"Could not locate element with selectors: {selectors}")


    def check_for_errors(self):
        try:
            # Check for error message displayed on the page
            error_element = self.driver.find_element(By.CSS_SELECTOR, ".flash-error") # Example error selector
            return error_element.text
        except NoSuchElementException:
            pass  # No error element found

        try:
            # Check for error in URL (e.g., after redirect)
            if "error" in self.driver.current_url.lower():
                return "Error in URL"
        except Exception as e:
            print(f"Error checking URL: {e}")

        try:
            # Check browser console for errors
            for entry in self.driver.get_log('browser'):
                if entry['level'] == 'SEVERE':
                    return entry['message']
        except Exception as e:
            print(f"Error checking browser console: {e}")
        
        return None  # No error detected


    def test_login_long_email(self):
        if not self.test_data:
            self.test_data = [{"email": "a"*300, "password": "testpassword"}] # Default values

        for data in self.test_data:
            email = data.get("email", "a"*300) # Default long email if not provided
            password = data.get("password", "testpassword")
            try:
                self.driver.get("https://github.com/login")
                email_field = self.locate_element({"id": "login_field"})
                email_field.send_keys(email)
                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(password)
                sign_in_button = self.locate_element({"css": "input[type='submit']"})
                sign_in_button.click()

                error_message = self.check_for_errors()
                self.assertTrue(error_message, "No error message displayed for long email")
                print(f"Test passed for email: {email[:20]}... (truncated)") # Truncate for display

            except Exception as e:
                print(f"Test failed: {e}")
                return False # Explicitly return False on failure

        return True # Return True if all tests pass


if __name__ == "__main__":
    test_result = unittest.main(exit=False).result
    if len(test_result.failures) == 0 and len(test_result.errors) == 0:
        exit(0)  # Exit code 0 for success
    else:
        exit(1)  # Exit code 1 for failure