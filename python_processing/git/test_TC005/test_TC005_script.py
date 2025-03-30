import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestNavigateToHome(unittest.TestCase):

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

    def test_navigate_to_home(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "testcase.json"), "r") as f:
                test_data = json.load(f)
        except FileNotFoundError:
            test_data = {}  # Use default values if file not found

        base_url = "https://incognito-three-chi.vercel.app/login"  # Default URL

        if test_data:
            # Iterate through test data sets if available
            for data_set in test_data.get("test_cases", []): # Assuming "test_cases" key holds an array of datasets
                if data_set.get("id") == "TC005":
                    base_url = data_set.get("url", base_url) # Override with data from file if present
                    break # Stop searching once the correct test case is found
        
        try:
            # Step 1: Navigate to the login page
            self.driver.get(base_url)

            # Step 2: Click the 'Incognito' logo
            logo_link = self.locate_element({"css": "a[href='/']"})
            logo_link.click()

            # Expected Result 1: User should be redirected to the home page.
            self.assertEqual(self.driver.current_url, "https://incognito-three-chi.vercel.app/")
            print("Test passed.")
            return True

        except Exception as e:
            print(f"Test failed: {e}")
            return False


if __name__ == "__main__":
    test_result = TestNavigateToHome().test_navigate_to_home()
    print(f"Overall test result: {'Pass' if test_result else 'Fail'}")