import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestSignUpNavigation(unittest.TestCase):

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

    def test_sign_up_navigation(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "testcase.json"), "r") as f:
                test_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            test_data = []  # Use default values if file not found or empty

        if not test_data:
            test_data = [{}] # Run at least once with default values

        for data in test_data:
            try:
                # Navigate to the login page
                self.driver.get("https://github.com/login")

                # Click the "Create an account" link
                create_account_link = self.locate_element({"css": "a[href*='/signup']"})
                create_account_link.click()

                # Assertion: Check if the URL contains '/signup' indicating successful redirection
                self.assertIn("/signup", self.driver.current_url, "Redirection to sign-up page failed.")
                print("Test passed for data set:", data)
                test_result = True

            except Exception as e:
                print(f"Test failed for data set: {data}. Error: {e}")
                test_result = False
                # You might want to add more detailed error handling or logging here.
                self.fail(str(e)) # Fail the test case

        return test_result # Return the final result after running all data sets



if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestSignUpNavigation('test_sign_up_navigation'))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test fails, 0 otherwise