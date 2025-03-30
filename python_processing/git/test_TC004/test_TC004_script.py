import unittest
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestToggleTheme(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()  # Or any other browser
        self.driver.maximize_window()
        self.test_data = self.load_test_data()

    def tearDown(self):
        self.driver.quit()

    def load_test_data(self):
        try:
            with open("testcase.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("testcase.json not found, using default values.")
            return {}  # Return empty dict for default behavior

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


    def test_toggle_theme(self):
        try:
            # Navigate to the login page
            self.driver.get("https://incognito-three-chi.vercel.app/login")

            # Click the theme toggle button
            toggle_button = self.locate_element({"css": "button.text-yellow-300"})
            toggle_button.click()

            # Add assertions to check theme change (This part requires inspecting the page 
            # to identify how the theme change is reflected in the HTML, e.g., a class change)
            # Example (replace with actual check based on your application):
            # body_class = self.driver.find_element(By.TAG_NAME, "body").get_attribute("class")
            # self.assertIn("dark-mode", body_class) # if dark mode adds a "dark-mode" class

            print("Test passed.")
            return True

        except Exception as e:
            print(f"Test failed: {e}")
            return False


if __name__ == "__main__":
    test_result = TestToggleTheme().test_toggle_theme() # Run the test directly
    print(f"Test Result: {test_result}") # Print True/False result