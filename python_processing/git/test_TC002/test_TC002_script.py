import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestFailedLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_data = []
        try:
            with open("testcase.json", "r") as f:
                testcase = json.load(f)
                self.test_data = testcase.get("test_data", [])
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
        if not self.test_data:
            self.test_data = [{"email": "invaliduser@example.com", "password": "wrongpassword"}]  # Default values

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


    def test_failed_login(self):
        overall_result = True
        for data in self.test_data:
            try:
                self.driver.get("https://github.com/login")
                email_field = self.locate_element({"id": "login_field"})
                email_field.send_keys(data["email"])
                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(data["password"])
                sign_in_button = self.locate_element({"css": ".js-sign-in-button"})
                sign_in_button.click()

                # Assertion: Check for error message (adjust selector if needed)
                error_message = self.locate_element({"css": ".flash-error"}) # Example selector
                self.assertTrue(error_message.is_displayed(), "Error message not displayed")
                print(f"Test passed for {data}")

            except Exception as e:
                print(f"Test failed for {data}: {e}")
                overall_result = False
        return overall_result



if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestFailedLogin))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if tests fail, 0 if pass