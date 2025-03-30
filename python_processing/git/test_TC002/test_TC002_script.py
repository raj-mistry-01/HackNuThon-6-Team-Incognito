import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestGithubLogin(unittest.TestCase):

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
            self.test_data = [{"email": "invaliduser@example.com", "password": "wrongpassword"}]

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
            except Exception:
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")

    def test_failed_login(self):
        overall_result = True
        for data in self.test_data:
            try:
                self.driver.get("https://github.com/login")
                email_field = self.locate_element({"id": "login_field"})
                email_field.send_keys(data.get("email", "invaliduser@example.com"))
                password_field = self.locate_element({"id": "password"})
                password_field.send_keys(data.get("password", "wrongpassword"))
                sign_in_button = self.locate_element({"css": ".js-sign-in-button"})
                sign_in_button.click()

                # Assertion: Check for error message (adjust selector if needed)
                error_message = self.locate_element({"css": ".flash-error"}) # Example error message selector
                self.assertTrue(error_message.is_displayed(), "Error message not displayed")
                print("Test Passed for data:", data)

            except Exception as e:
                print(f"Test Failed for data: {data}. Error: {e}")
                overall_result = False

        return overall_result  # Return overall result (True if all passed, False otherwise)



if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestGithubLogin))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise