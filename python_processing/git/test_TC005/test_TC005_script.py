import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestNavigateToCreateAccount(unittest.TestCase):

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

    def test_navigate_to_create_account(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f)
        except FileNotFoundError:
            test_data = {}  # Use default values if file not found

        if not test_data:
            test_cases = [{}] # Run with default values if file is empty or no data
        else:
            test_cases = [test_data] # Run with the data from the file

        overall_result = True
        for test_case in test_cases:
            try:
                self.driver.get("https://github.com/login")

                # Step 1: Click the 'Create an account' link
                create_account_link = self.locate_element(test_case.get("elements", [{"css": ".login-callout a[href*='/signup']"}] )[0].get("selectors"))
                create_account_link.click()

                # Expected Result 1: User is redirected to the sign-up page.
                self.assertTrue("signup" in self.driver.current_url, "User was not redirected to the signup page.")
                print("Test passed for test case:", test_case.get("id", "Default"))

            except Exception as e:
                print(f"Test failed: {e}")
                overall_result = False

        return overall_result


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestNavigateToCreateAccount))
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(test_suite)
    exit(not test_result.wasSuccessful()) # Exit with 1 if tests fail, 0 if they pass