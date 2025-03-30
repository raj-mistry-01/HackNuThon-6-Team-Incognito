
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
    print(f"\nRunning test: {test_info['test_name']} ({test_info['test_id']})")
    
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
        
    print(f"\n--- Test Execution Report ---")
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
