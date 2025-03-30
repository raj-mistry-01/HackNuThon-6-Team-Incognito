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

# Configuration variables - Edit these values
WEBSITE_URL = "https://github.com/login"  # URL of the website to scrape
OUTPUT_FOLDER = "./git"  # Folder to store generated test scripts
API_KEYS = ["AIzaSyDQd8ihGxz2bCA9lH-5pyyKYQjgIyolI3E", "AIzaSyCF6R7qDpglneMDgYun360O52A_UUeO-QM", "AIzaSyAETp5SEGNHvgfTlDizjfG8Bub16vh-D5w"]  # Replace with your three Google Gemini API keys
MAX_BATCHES = 3  # Maximum number of API calls for test generation

# Ensure output directory exists
def ensure_output_dir():
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

# Utility functions
def save_json_to_file(data, file_path, indent=2):
    """Save JSON data to a file"""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=indent)
    print(f"Successfully saved data to {file_path}")

def extract_json_from_response(response_text):
    """Extract JSON from a text response that may contain markdown code blocks"""
    if not response_text:
        print("Error: Empty response received from API.")
        return None

    try:
        # Try to parse as JSON directly
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass
        else:
            json_match = re.search(r'json\s*(.*?)\s*', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1).strip())
                except json.JSONDecodeError:
                    pass
            else:
                json_match = re.search(r'{.*}', response_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0).strip())
                    except json.JSONDecodeError:
                        pass
        print(f"Error: Could not extract JSON from response. Raw response: {response_text}")
        return None

def extract_code(response_text):
    """Extract clean code from a response that may contain markdown code blocks"""
    # Look for Python code blocks
    code_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    # Look for any code blocks
    code_match = re.search(r'```(.*?)```', response_text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    # Return cleaned text
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

    # Configure Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Launch Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)

        # Wait for JavaScript to load (adjust timeout as needed)
        time.sleep(5)  # Allow time for dynamic content to load

        # Get the complete HTML
        html_content = driver.page_source

        # Save the HTML content to a file
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
        generation_config={"temperature": 0.2},
        system_instruction="""
        You are a web testing expert who analyzes HTML content to create meaningful test cases.

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
        - You MUST use selector values that ACTUALLY EXIST in the HTML
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
    return extract_json_from_response(response.text)

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

def create_test_runner(output_path, generated_scripts):
    """Create a test runner script that will run all test scripts and generate a report"""
    runner_code = '''
import os
import sys
import json
import time
import importlib.util
from datetime import datetime
from pathlib import Path

def load_module_from_path(path, module_name):
    """Load a Python module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_test(test_info):
    """Run a single test and return the result"""
    print(f"\\nRunning test: {test_info['test_name']} ({test_info['test_id']})")
    
    try:
        # Load the test module
        script_path = test_info['script_path']
        module_name = f"test_{test_info['test_id']}"
        
        # Check if the script exists
        if not os.path.exists(script_path):
            print(f"Error: Test script not found at {script_path}")
            return False
            
        # Add the script's directory to sys.path
        script_dir = os.path.dirname(script_path)
        if script_dir not in sys.path:
            sys.path.append(script_dir)
            
        # Load and run the test module
        module = load_module_from_path(script_path, module_name)
        
        # Find the test class (should inherit from unittest.TestCase)
        test_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and 'TestCase' in str(obj.__bases__):
                test_class = obj
                break
                
        if test_class is None:
            print(f"Error: No TestCase class found in {script_path}")
            return False
            
        # Create an instance and run the test
        test_instance = test_class()
        
        # Call setUp, runTest/test_method, and tearDown
        try:
            if hasattr(test_instance, 'setUp'):
                test_instance.setUp()
                
            # Find test methods
            test_methods = [method for method in dir(test_instance) 
                           if method.startswith('test') and callable(getattr(test_instance, method))]
            
            if not test_methods:
                if hasattr(test_instance, 'runTest'):
                    test_methods = ['runTest']
                else:
                    print(f"Error: No test methods found in {script_path}")
                    return False
            
            # Run all test methods
            results = []
            for method in test_methods:
                try:
                    result = getattr(test_instance, method)()
                    if result is None:  # If no explicit return, assume success
                        result = True
                    results.append(result)
                except Exception as e:
                    print(f"Error running test method {method}: {e}")
                    results.append(False)
            
            # Test passes if all methods pass
            return all(results)
            
        except Exception as e:
            print(f"Error running test: {e}")
            return False
            
        finally:
            if hasattr(test_instance, 'tearDown'):
                try:
                    test_instance.tearDown()
                except Exception as e:
                    print(f"Error in tearDown: {e}")
            
    except Exception as e:
        print(f"Error importing or running test module: {e}")
        return False

def run_all_tests(test_infos):
    """Run all tests and generate a report"""
    results = []
    start_time = datetime.now()
    
    for test_info in test_infos:
        test_result = {
            "test_id": test_info["test_id"],
            "test_name": test_info["test_name"],
            "script_path": test_info["script_path"],
            "testcase_path": test_info["testcase_path"],
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "passed": False
        }
        
        try:
            test_result["passed"] = run_test(test_info)
        except Exception as e:
            print(f"Error running test {test_info['test_id']}: {e}")
            test_result["error"] = str(e)
            
        test_result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results.append(test_result)
        
        # Print result
        status = "PASSED" if test_result["passed"] else "FAILED"
        print(f"Test {test_info['test_id']} {status}")
        
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Generate report
    report = {
        "execution_date": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_duration_seconds": duration,
        "total_tests": len(results),
        "passed_tests": sum(1 for r in results if r["passed"]),
        "failed_tests": sum(1 for r in results if not r["passed"]),
        "results": results
    }
    
    # Save report
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\\n--- Test Execution Report ---")
    print(f"Total tests: {report['total_tests']}")
    print(f"Passed: {report['passed_tests']}")
    print(f"Failed: {report['failed_tests']}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Report saved to report.json")
    
    return report

if __name__ == "__main__":
    # Get the current directory where this script is running
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load test index from the current directory
    index_path = os.path.join(current_dir, "test_index.json")
    
    try:
        with open(index_path, "r") as f:
            test_index = json.load(f)
        
        test_infos = test_index.get("generated_scripts", [])
        if not test_infos:
            print("No tests found in test_index.json")
            sys.exit(1)
            
        # Run all tests
        run_all_tests(test_infos)
        
    except FileNotFoundError:
        print(f"Error: Test index file not found at {index_path}")
        print("Please run the main script first to generate test files.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)
'''
    runner_path = output_path / "run_all_tests.py"
    with open(runner_path, 'w') as file:
        file.write(runner_code)
    
    print(f"Created test runner script at {runner_path}")

def main_fn():
    """Main execution function"""
    output_folder = ensure_output_dir()
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
            create_test_runner(output_path, generated_scripts)
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
    main_fn()