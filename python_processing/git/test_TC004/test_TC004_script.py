import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestCreateAccountNavigation(unittest.TestCase):

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

    def test_create_account_navigation(self):
        try:
            with open("testcase.json", "r") as f:
                test_data = json.load(f)
        except FileNotFoundError:
            test_data = []  # Use default values if file not found

        if not test_data:
            test_data = [{}] # Run at least once with default values

        overall_result = True
        for data in test_data:
            try:
                self.driver.get("https://github.com/login")

                # Step 1: Click the 'Create an account' link
                create_account_link = self.locate_element({"css": "a[href^='/signup']", "xpath": "//a[contains(@href, '/signup')]"}, 10)
                create_account_link.click()

                # Expected Result 1: User is redirected to the account creation page.
                self.assertIn("signup", self.driver.current_url)
                print("Test passed for dataset:", data)

            except Exception as e:
                print(f"Test failed for dataset: {data}. Error: {e}")
                overall_result = False

        return overall_result


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestCreateAccountNavigation))
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(test_suite)
    exit(not test_result.wasSuccessful()) # Exit with 1 if tests fail, 0 if they pass