import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class TestGithubLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.get("https://github.com/login")
        self.test_data = self.load_test_data()

    def tearDown(self):
        self.driver.quit()

    def load_test_data(self):
        try:
            with open("testcase.json", "r") as f:
                data = json.load(f)
                return data.get("test_data", [])  # Extract test_data, default to empty list if not found
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
            return [{"email": "' OR '1'='1", "password": "password"}]  # Default values

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
                elif selector_type == "type": # Added for 'type' selector
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[type="{selector_value}"]')))
            except (NoSuchElementException, TimeoutException):
                continue
        raise Exception(f"Could not locate element with selectors: {selectors}")


    def check_for_errors(self):
        # Check for URL errors (e.g., error parameters)
        if "error" in self.driver.current_url.lower():
            return False

        # Check for console errors
        for entry in self.driver.get_log('browser'):
            if entry['level'] == 'SEVERE':  # Or other relevant levels
                return False
        
        # Check for error messages within specific elements (adapt as needed)
        try:
            error_element = self.driver.find_element(By.CSS_SELECTOR, ".flash-error") # Example
            if error_element.is_displayed():
                return False
        except NoSuchElementException:
            pass  # No error element found

        return True  # No errors detected



    def test_sql_injection(self):
        overall_result = True
        for data in self.test_data:
            try:
                email_field = self.locate_element({"id": "login_field"})
                email_field.clear()
                email_field.send_keys(data["email"])

                password_field = self.locate_element({"id": "password"})
                password_field.clear()
                password_field.send_keys(data["password"])

                sign_in_button = self.locate_element({"type": "submit"})
                sign_in_button.click()

                if not self.check_for_errors():
                    print(f"Test failed for data: {data}")
                    overall_result = False
                else:
                    print(f"Test passed for data: {data}")

            except Exception as e:
                print(f"Test failed with exception: {e}")
                overall_result = False

        print(f"Overall test result: {'Pass' if overall_result else 'Fail'}")
        return overall_result



if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestGithubLogin))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if tests fail, 0 if pass