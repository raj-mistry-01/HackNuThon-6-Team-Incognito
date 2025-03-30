import os
import sys
import json
import time
import importlib.util
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

def load_module_from_path(path, module_name):
    """Load a Python module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_test_case(test_id, test_info):
    """Run a single test case and return result"""
    print(f"\nRunning test: {test_info['test_name']} ({test_id})")
    
    try:
        script_path = test_info['script_path']
        module_name = f"test_{test_id}"
        
        if not os.path.exists(script_path):
            return {"test_case": test_id, "status": "FAILED", "error": "Test script not found", "url": script_path}
        
        module = load_module_from_path(script_path, module_name)
        
        test_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and 'TestCase' in str(obj.__bases__):
                test_class = obj
                break
                
        if test_class is None:
            return {"test_case": test_id, "status": "FAILED", "error": "No TestCase class found", "url": script_path}
        
        test_instance = test_class()
        
        if hasattr(test_instance, 'setUp'):
            test_instance.setUp()
            
        test_methods = [method for method in dir(test_instance) 
                        if method.startswith('test') and callable(getattr(test_instance, method))]
        
        if not test_methods:
            if hasattr(test_instance, 'runTest'):
                test_methods = ['runTest']
            else:
                return {"test_case": test_id, "status": "FAILED", "error": "No test methods found", "url": script_path}
        
        results = []
        for method in test_methods:
            try:
                result = getattr(test_instance, method)()
                results.append(result if result is not None else True)
            except Exception:
                results.append(False)
        
        passed = all(results)
        return {"test_case": test_id, "status": "PASSED" if passed else "FAILED", "url": script_path}
    
    except Exception as e:
        return {"test_case": test_id, "status": "FAILED", "error": str(e), "url": script_path}

def run_all_tests(test_infos):
    """Run all tests in parallel using multiple processes and generate a report"""
    start_time = datetime.now()
    results = []
    max_workers = min(os.cpu_count(), len(test_infos)) 
    
    print(f"Running tests in parallel with {max_workers} processes...\n")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_test = {executor.submit(run_test_case, i, case): i for i, case in enumerate(test_infos, start=1)}
        
        for future in as_completed(future_to_test):
            results.append(future.result())
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    report = {
        "execution_date": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_duration_seconds": duration,
        "total_tests": len(results),
        "passed_tests": sum(1 for res in results if res["status"] == "PASSED"),
        "failed_tests": sum(1 for res in results if res["status"] == "FAILED"),
        "results": results
    }
    
    with open("report.json", "w") as f:
        json.dump(report, f, indent=4)
    
    print("\n--- Test Execution Summary ---")
    print(f"\nTotal tests: {report['total_tests']}")
    print(f"Passed: {report['passed_tests']}")
    print(f"Failed: {report['failed_tests']}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Report saved to report.json")
    
    return report

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "test_index.json")
    
    try:
        with open(index_path, "r") as f:
            test_index = json.load(f)
        
        test_infos = test_index.get("generated_scripts", [])
        if not test_infos:
            print("No tests found in test_index.json")
            sys.exit(1)
            
        run_all_tests(test_infos)
        
    except FileNotFoundError:
        print(f"Error: Test index file not found at {index_path}")
        print("Please run the main script first to generate test files.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)