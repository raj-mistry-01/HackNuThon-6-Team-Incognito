import os
import time
import json
import re
import unittest
from pathlib import Path
from math import ceil
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import importlib.util
import sys
from multiprocessing import Process, Queue
from figma_extraction import get_figma_json
FIGMA_ACCESS_TOKEN = "figd_uVoIukrCAalpz9okHu4CEcG9nHcXCD1YzXHutjcR"
FILE_ID = "zMlGokdmscjtOPXlwzk4Fi"
WEBSITE_URL = "https://uniboxlogin.wifi-soft.com//portals/NU-Student/index.php?sid=q4eet6s0fuuod9rkligp5885u6&sidub=q4eet6s0fuuod9rkligp5885u6&mac=3C-E9-F7-D3-0F-7C"  # URL of the website to scrape
OUTPUT_FOLDER = "./testing"  # Folder to store generated test scripts
# 1
# API_KEYS = ["AIzaSyBOQMW2MWVtkbIALSeFGjOg5ny9GQmPfTA", "AIzaSyC9sMyfAAapqttB1jNBuYBj4aqUshC1-Sk", "AIzaSyDB6rWqA1PEaux2qizqX9r9EDP12houoSY"]  # Replace with your three Google Gemini API keys

# 2
# API_KEYS = ["AIzaSyAe1VXuS-FRe_JscLDEss1iICB2s0zItAw", "AIzaSyD9XaO5jacOs4_MtLHGoO_IJzbsX63x1u8", "AIzaSyBXVJwIaNeEsbqAYnmvmM1rGkH1ElNKVmM"]  # Replace with your three Google Gemini API keys

# 3
# API_KEYS = ["AIzaSyBXVJwIaNeEsbqAYnmvmM1rGkH1ElNKVmM", "AIzaSyAB52eRWrAudeIraPEBu-p-lcfEHPp4Z1E", "AIzaSyA3wmhd6LxxLtfaYnxb-_kAwBrEkswbOYI"]  # Replace with your three Google Gemini API keys

# 4 
API_KEYS = ["AIzaSyD2wsIV48Afsbpvbx-VjlAFsU6fpxyEy_w", "AIzaSyD9kkbri5EaQGklDrPue2TVki6CNW6VI1w", "AIzaSyDG5AGJvOh19ZuqLDMzIeOiFI1b4GyGKQI"]  # Replace with your three Google Gemini API keys

# 5 
# API_KEYS = ["AIzaSyCrV3zu_jWyLXMwV3iPh0p9M-XO7oqn3_w", "AIzaSyAbm-VkuoDsiMhHjmCJIQTfeEsL9MQSAvY", "AIzaSyDfLXaOyNk0ranGuyEJRVqFrq0Xj59KDys"]  # Replace with your three Google Gemini API keys

# 6 
# API_KEYS = ["AIzaSyAzMJSewFIWc8JsLLKW4cgU1sc_Ng9NoyY", "AIzaSyAq5DHAea98LLoG-hNOZztVTNGZkFgCOVI", "AIzaSyC5fZ7NMqBYYZt7zMPRTdyMUBO0wQQwyOw"]  # Replace with your three Google Gemini API keys

# 7
# API_KEYS = ["AIzaSyAe1VXuS-FRe_JscLDEss1iICB2s0zItAw", "AIzaSyD9XaO5jacOs4_MtLHGoO_IJzbsX63x1u8", "AIzaSyBXVJwIaNeEsbqAYnmvmM1rGkH1ElNKVmM"]  # Replace with your three Google Gemini API keys

# 8
# API_KEYS = ["AIzaSyAkVrXNvpnkbka-eGGsNjm6nk-iF89dWQI", "AIzaSyBABWnwOaQlPtEkcnKFLHpJCMEtsCFe3dk", "AIzaSyBAiPrGh06ZBq6M6T5NY0wrLYyyTo3mQgQ"]

# 9
# API_KEYS = ["AIzaSyA7B8BTgsLXvV5TzvIU1acTi8NSygM4ceE", "AIzaSyCQwCbJbR6SqlZNh-EeFYM8q_8hek-KJxg", "AIzaSyCGr743jJaGBYdJBemxOl7_eHwLjww_ddA"]  # Replace with your three Google Gemini API keys
MAX_BATCHES = 3  # Maximum number of API calls for test generation
def ensure_output_dir():
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path
def save_json_to_file(data, file_path, indent=2):
    """Save JSON data to a file"""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=indent)
    print(f"Successfully saved data to {file_path}")

def extract_json_from_text(text):
    """
    Extract JSON from text that might contain markdown formatting or other text.
    This handles cases where JSON is wrapped in ```json ... ``` blocks or other formatting.
    """
    # First try to find JSON within markdown code blocks
    json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    matches = re.findall(json_pattern, text)
    
    if matches:
        # Try each match until we find valid JSON
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    # If no markdown blocks or none contained valid JSON, try treating the whole text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # As a last resort, try to find anything that looks like a JSON object
    json_object_pattern = r'(\{[\s\S]*\})'
    object_matches = re.findall(json_object_pattern, text)
    
    if object_matches:
        for match in object_matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    # If all attempts fail, raise an exception
    raise ValueError("No valid JSON found in the text")

def extract_code(response_text):
    """Extract clean code from a response that may contain markdown code blocks"""
    # Look for Python code blocks
    code_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    code_match = re.search(r'```(.*?)```', response_text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    return response_text.strip()
def configure_genai(api_key):
    """Configure the Gemini API with the provided API key"""
    genai.configure(api_key=api_key)
def scrape_website_html(url, output_folder):
    """
    Scrape dynamic HTML from a website using Selenium
    Args:
        url: URL of the website to scrape
        output_folder: Folder to save the scraped HTML
    Returns:
        str: HTML content of the website
    """
    print(f"Scraping dynamic HTML from: {url}")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        time.sleep(5)  
        html_content = driver.page_source
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        html_path = output_path / "scraped_website_dynamic.html"
        with open(html_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"✅ Successfully scraped dynamic HTML and saved to {html_path}")
        return html_content
    except Exception as e:
        print(f"❌ Error scraping website: {e}")
        return None
    finally:
        driver.quit()
def generate_test_cases(html_content):
    """Generate test cases from HTML content using Gemini API"""
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={"temperature": 0.3},
        system_instruction="""
        You are a web testing expert who analyzes HTML content to create meaningful test cases.
        i want u to generate the testcase which will look for the edge case where the ui get failed
        like like email id with space , very long email id, domain less email id, pasword missing,etc
        no need to make a test case of the valid passward and invalid password
        in genral i want  the test case that will actully push the limit of the ui 
        not just in the login page but it should be versetile in every ui testing
        do not genrate the simple test case like button clickable or exist or some easy test case
        the test case must be very hard no simple testcases should be entertained also include SQL INJECTION wherever nedeed
        First, identify the key features and interactive elements from the HTML content.
        Then, create test cases for these features, focusing on:
        1. Critical user flows (login, sign up, navigation)
        2. Form submissions
        3. Button interactions
        4. Data display and validation
        For each test case:
        1. Create clear steps that can be automated
        2. Identify the HTML elements needed for each step
        3. Provide reliable selectors for each element
        EXTREMELY IMPORTANT:
        -i want u to generate the testcase which will look for the edge case where the ui get failed
        like like email id with space , very long email id, domain less email id, pasword missing,etc
        no need to make a test case of the valid passward and invalid password 
        - You MUST use selector values that ACTUALLY EXIST in the HTML
        - you must think of all the aspects 
        - PRIORITIZE elements with IDs - these provide the most reliable selectors
        - Never invent or guess selectors - they must be extracted from the provided HTML
        - For elements without IDs, provide multiple selector alternatives (CSS, XPath)
        For login forms, provide multiple test cases with different email and password combinations.
        Return a JSON with this structure:
        {
            "test_cases": [
                {
                    "id": "TC001",
                    "name": "Descriptive test name",
                    "description": "What this test verifies",
                    "steps": ["Step 1: Action description", "Step 2: Action description"],
                    "expected_results": ["Expected result 1", "Expected result 2"],
                    "elements": [
                        {
                            "step": "The step this element belongs to",
                            "description": "Element description",
                            "type": "button|input|form|etc",
                            "text_content": "Text content if relevant",
                            "selectors": {
                                "id": "element-id",
                                "css": "css-selector",
                                "xpath": "xpath-expression",
                                "name": "name-attribute"
                            }
                        }
                    ],
                    "test_data": [
                        {
                            "email": "test@example.com",
                            "password": "password123"
                        },
                        {
                            "email": "invalid@example.com",
                            "password": "wrongpassword"
                        }
                    ]
                }
            ]
        }
        Create 5-10 test cases that cover the core functionality visible in the HTML.
        ONLY include selectors that ACTUALLY EXIST in the HTML.
        """
    )
    prompt = f"""
    Analyze this HTML content and create 5-10 test cases with their required elements:
    HTML Content:
    {html_content}
    i want u to generate the testcase which will look for the edge case where the ui get failed
        like like email id with space , very long email id, domain less email id, pasword missing,etc
        no need to make a test case of the valid passward and invalid password inlcude SQL  Injection whever needed
    For each test case:
    1. Identify the user flow or feature being tested
    2. Create clear steps that can be automated
    3. Identify the specific HTML elements needed for each step
    4. Provide reliable selectors (IDs, CSS selectors, XPath) for each element
    For login forms, provide multiple test data combinations (valid credentials, invalid credentials, etc.)
    ONLY use selectors that ACTUALLY EXIST in the HTML. Prioritize elements with IDs.
    Include 5-10 test cases that cover the core functionality visible in the HTML.
    """
    response = model.generate_content(prompt)
    return extract_json_from_text(response.text)
def generate_selenium_script(test_case, website_url):
    """Generate Selenium script for a test case using Gemini API"""
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={"temperature": 0.2},
        system_instruction="""
        You are a QA automation engineer who creates detailed Selenium Python test scripts.
        Generate high-quality, maintainable Python scripts using Selenium WebDriver.
        Your scripts must:
        1. Properly handle testcase.json file loading to get test data
        2. Include setup with webdriver initialization
        3. Include teardown that closes the browser
        4. Have well-structured test methods with descriptive names
        5. Include proper error handling with try/except blocks
        6. Use explicit waits for elements
        7. Include appropriate assertions that check expected results
        8. Add descriptive comments explaining each step
        VERY IMPORTANT: Each script should:
        1. Look for a corresponding testcase.json file in the same folder
        2. Read test data from that file (credentials, input values, etc.)
        3. Run the test with each set of test data if available
        4. If the testcase.json is empty or not found, the script should run with default values
        5. the script must listen for every type of erorr a website can throw like some website throw error in the console, some show error inn the url, some show a new error div
        so write a deep logic for the error detection whch can listen for different type of error
        Use the EXACT selectors provided for each element:
        - PRIORITIZE using ID selectors whenever available
        - If no ID exists, use a reliable CSS selector or XPath as provided
        - NEVER try to use generic XPath searches like "//*[contains(text(), 'Some Text')]"
        - NEVER use frame or iframe switching unless explicitly mentioned in the element selectors
        Format each test as a complete Python class inheriting from unittest.TestCase and ensure it can be run independently.
        Each script should return True for test pass or False for test failure.
        """
    )

    script_prompt = f"""
    Generate a Selenium Python test script for this test case:

    Website URL: {website_url}

    Test Case with Element Selectors:
    {json.dumps(test_case, indent=2)}

    Create a complete Python unittest class that:
    1. Reads test data from a testcase.json file in the same directory
    2. Runs the test for each set of test data in the testcase.json file
    3. If testcase.json is empty or missing, runs with default values
    4. Returns test results (True for pass, False for fail)

    EXTREMELY IMPORTANT: The script must:
    1. Use the exact selectors provided in the test case
    2. Include a locate_element helper method for element interaction
    3. Include proper setup/teardown methods
    4. Add try/except blocks for error handling
    5. Include assertions that verify expected results
    6. Write results to the console

    Include a helper method like this:

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
        raise Exception(f"Could not locate element with selectors: {{selectors}}")

    Make sure your script includes a way to run it directly (if __name__ == '__main__') and returns True/False results.
    """
    response = model.generate_content(script_prompt)
    return extract_code(response.text)

def worker(task_queue, result_queue, api_key):
    """Worker process function to handle API tasks with its own API key"""
    import google.generativeai as genai
    configure_genai(api_key)
    while True:
        task = task_queue.get()
        if task is None:  # Sentinel to stop the worker
            break
        task_type = task['type']
        if task_type == 'extract':
            html_content = task['html_content']
            all_test_cases_path = task['all_test_cases_path']
            test_cases_with_elements = generate_test_cases(html_content)
            if test_cases_with_elements:
                save_json_to_file(test_cases_with_elements, all_test_cases_path)
                result_queue.put({'type': 'extract_result', 'test_cases_with_elements': test_cases_with_elements})
            else:
                result_queue.put({'type': 'extract_result', 'test_cases_with_elements': None})
        elif task_type == 'generate_script':
            test_case = task['test_case']
            website_url = task['website_url']
            script_path = task['script_path']
            code = generate_selenium_script(test_case, website_url)
            if code:
                with open(script_path, 'w') as file:
                    file.write(code)

def extract_html_elements(html_content, output_folder):
    """
    Extract relevant HTML elements directly from website HTML

    Args:
        html_content: HTML content of the website
        output_folder: Folder to save extracted elements

    Returns:
        dict: HTML elements for generated test cases
    """
    print(f"Extracting HTML elements directly from website content...")

    # Parse HTML with BeautifulSoup for analysis
    soup = BeautifulSoup(html_content, 'html.parser')
    output_path = Path(output_folder)

    # Extract all unique selectors with more detail
    all_elements = []

    # Extract elements with ID - prioritize these
    for element in soup.select('[id]'):
        all_elements.append({
            "element_type": element.name,
            "id": element.get('id'),
            "classes": element.get('class', []),
            "text": element.text.strip() if len(element.text.strip()) < 50 else element.text.strip()[:50] + "...",
            "attributes": {k: v for k, v in element.attrs.items() if k not in ['id', 'class']}
        })

    # Extract interactive elements without ID but with classes or other attributes
    for selector in ['button', 'input', 'form', 'a', 'select', 'textarea', 'div', 'span']:
        for element in soup.select(f'{selector}:not([id])'):
            attributes = {k: v for k, v in element.attrs.items() if k != 'class'}
            if element.get('class') or attributes:
                all_elements.append({
                    "element_type": element.name,
                    "id": None,
                    "classes": element.get('class', []),
                    "text": element.text.strip() if len(element.text.strip()) < 50 else element.text.strip()[:50] + "...",
                    "attributes": attributes
                })

    # Save all extracted elements for reference
    all_selectors_path = output_path / "all_html_selectors.json"
    save_json_to_file({"elements": all_elements}, all_selectors_path)

    print(f"Saved {len(all_elements)} HTML elements to {all_selectors_path}")

    # Now generate test cases directly from HTML structure
    # This part is moved to the worker process via task queue
    return None  # Placeholder; actual result comes from worker

def generate_individual_test_files(test_cases_with_elements, website_url, output_folder):
    """
    Generate individual testcase.json and Selenium script for each test case

    Args:
        test_cases_with_elements: Test cases with HTML elements
        website_url: URL of the website to test
        output_folder: Folder to save generated test scripts and data

    Returns:
        list: Generated test scripts information
    """
    print(f"Generating individual test files for each test case...")

    # Create output folder
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    test_cases = test_cases_with_elements.get("test_cases", [])
    if not test_cases:
        print("No test cases to process.")
        return []

    generated_scripts = []

    # Process each test case individually
    for test_case in test_cases:
        test_id = test_case.get("id", "unknown")
        test_name = test_case.get("name", "Unknown Test")
        print(f"Generating files for test case: {test_id} - {test_name}")

        # Create test case directory
        test_dir = output_path / f"test_{test_id}"
        test_dir.mkdir(parents=True, exist_ok=True)

        # Save individual testcase.json file
        testcase_json_path = test_dir / "testcase.json"
        save_json_to_file(test_case, testcase_json_path)

        # Script generation is handled by workers
        script_filename = f"test_{test_id}_script.py"
        script_path = test_dir / script_filename

        generated_scripts.append({
            "test_id": test_id,
            "test_name": test_name,
            "script_path": str(script_path),
            "testcase_path": str(testcase_json_path),
            "directory": str(test_dir)
        })

    return generated_scripts

def main(WEBSITE_URL):
    """Main execution function"""
    output_folder = ensure_output_dir()
    get_figma_json(FIGMA_ACCESS_TOKEN , FILE_ID)
    html_content = scrape_website_html(WEBSITE_URL, OUTPUT_FOLDER)
    if html_content:
        # Set up multiprocessing
        task_queue = Queue()
        result_queue = Queue()
        workers = []
        for api_key in API_KEYS:
            p = Process(target=worker, args=(task_queue, result_queue, api_key))
            p.start()
            workers.append(p)

        # Extract elements and prepare for test case generation
        soup = BeautifulSoup(html_content, 'html.parser')
        output_path = Path(output_folder)
        all_elements = []
        for element in soup.select('[id]'):
            all_elements.append({
                "element_type": element.name,
                "id": element.get('id'),
                "classes": element.get('class', []),
                "text": element.text.strip() if len(element.text.strip()) < 50 else element.text.strip()[:50] + "...",
                "attributes": {k: v for k, v in element.attrs.items() if k not in ['id', 'class']}
            })
        for selector in ['button', 'input', 'form', 'a', 'select', 'textarea', 'div', 'span']:
            for element in soup.select(f'{selector}:not([id])'):
                attributes = {k: v for k, v in element.attrs.items() if k != 'class'}
                if element.get('class') or attributes:
                    all_elements.append({
                        "element_type": element.name,
                        "id": None,
                        "classes": element.get('class', []),
                        "text": element.text.strip() if len(element.text.strip()) < 50 else element.text.strip()[:50] + "...",
                        "attributes": attributes
                    })
        all_selectors_path = output_path / "all_html_selectors.json"
        save_json_to_file({"elements": all_elements}, all_selectors_path)
        print(f"Saved {len(all_elements)} HTML elements to {all_selectors_path}")

        # Submit 'extract' task for test case generation
        all_test_cases_path = str(output_path / "all_test_cases.json")
        task_queue.put({
            'type': 'extract',
            'html_content': html_content,
            'all_test_cases_path': all_test_cases_path
        })

        # Wait for test case generation result
        while True:
            result = result_queue.get()
            if result['type'] == 'extract_result':
                test_cases_with_elements = result['test_cases_with_elements']
                break

        if test_cases_with_elements:
            # Generate individual test files
            generated_scripts = generate_individual_test_files(test_cases_with_elements, WEBSITE_URL, OUTPUT_FOLDER)

            # Submit script generation tasks
            for script_info in generated_scripts:
                task_queue.put({
                    'type': 'generate_script',
                    'test_case': test_cases_with_elements['test_cases'][int(script_info['test_id'].replace('TC', '')) - 1],
                    'website_url': WEBSITE_URL,
                    'script_path': script_info['script_path']
                })

            # Put sentinels to stop workers
            for _ in range(len(API_KEYS)):
                task_queue.put(None)

            # Wait for all workers to finish
            for p in workers:
                p.join()

            # Finalize with test runner and index
            # create_test_runner(output_path, generated_scripts)
            index_file_path = output_path / "test_index.json"
            save_json_to_file({
                "generated_scripts": generated_scripts,
                "total_count": len(generated_scripts),
                "website_url": WEBSITE_URL,
                "generation_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }, index_file_path)
            print(f"Successfully generated {len(generated_scripts)} test script packages in {output_folder}")
        else:
            print("Failed to generate test cases from HTML content")

if __name__ == "__main__":
    main(WEBSITE_URL="")