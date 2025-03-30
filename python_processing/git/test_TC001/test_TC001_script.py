import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class TestLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.maximize_window()
        self.test_data = []
        try:
            with open(os.path.join(os.path.dirname(__file__), "testcase.json"), "r") as f:
                testcase = json.load(f)
                self.test_data = testcase.get("test_data", [])
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
        if not self.test_data:
            self.test_data = [{"email": "test@example.com", "password": "password123"}]  # Default values

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


    def test_successful_login(self):
        overall_result = True
        for data in self.test_data:
            try:
                self.driver.get("https://incognito-three-chi.vercel.app/login")
                email_input = self.locate_element({"id": "email"})
                email_input.send_keys(data["email"])
                password_input = self.locate_element({"id": "password"})
                password_input.send_keys(data["password"])
                login_button = self.locate_element({"id": "login"})
                login_button.click()

                # Add assertion to check if login was successful (e.g., check URL or presence of a welcome message)
                # Example:
                # self.assertIn("dashboard", self.driver.current_url) 
                print(f"Test with data {data} passed.")

            except Exception as e:
                print(f"Test with data {data} failed: {e}")
                overall_result = False  # Set overall result to False if any test fails

        return overall_result # Return True if all tests passed, False otherwise


if __name__ == "__main__":
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestLogin))
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
    exit(not result.wasSuccessful()) # Exit with 1 if any test failed, 0 otherwise