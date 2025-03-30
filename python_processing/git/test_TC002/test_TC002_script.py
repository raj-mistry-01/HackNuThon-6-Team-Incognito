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
            except Exception:
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")

    def test_failed_login(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "testcase.json"), "r") as f:
                test_data_list = json.load(f).get("test_data", [])
        except FileNotFoundError:
            test_data_list = []

        if not test_data_list:
            test_data_list = [{"email": "invaliduser", "password": "wrongpassword"}]  # Default values

        overall_result = True
        for test_data in test_data_list:
            try:
                email = test_data["email"]
                password = test_data["password"]

                # Step 1: Enter invalid username/email
                username_field = self.locate_element({"id": "login_field", "css": "#login_field", "xpath": "//input[@id='login_field']"})
                username_field.send_keys(email)

                # Step 2: Enter invalid password
                password_field = self.locate_element({"id": "password", "css": "#password", "xpath": "//input[@id='password']"})
                password_field.send_keys(password)

                # Step 3: Click Sign in
                sign_in_button = self.locate_element({"css": ".js-sign-in-button", "xpath": "//input[@value='Sign in']"})
                sign_in_button.click()

                # Expected Result: Error message displayed
                error_message = self.locate_element({"id": "js-flash-container"}, wait_time=5) # Short wait for error
                self.assertTrue(error_message.is_displayed(), "Error message not displayed")
                print(f"Test Passed for {email}:{password}")


            except Exception as e:
                print(f"Test Failed for {email}:{password}: {e}")
                overall_result = False

        return overall_result



if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestGithubLogin))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if tests fail, 0 if pass