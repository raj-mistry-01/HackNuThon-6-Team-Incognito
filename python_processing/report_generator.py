import xml.etree.ElementTree as ET
import json

# ✅ Load test results from JSON file
with open("test_results.json", "r") as f:
    results = json.load(f)

# ✅ Create the JUnit XML structure
testsuite = ET.Element("testsuite", name="SeleniumTests", tests=str(len(results)), errors="0", failures="0")

failures = 0

for result in results:
    testcase = ET.SubElement(testsuite, "testcase", classname="TestSuite", name=f"Test {result['test_case']}")
    
    if result["status"] == "FAILED":
        failure = ET.SubElement(testcase, "failure", message="Test failed")
        failure.text = f"Expected URL not found. Got: {result['url']}"
        failures += 1

# ✅ Update the failure count in the root element
testsuite.set("failures", str(failures))

# ✅ Write the XML report
tree = ET.ElementTree(testsuite)
tree.write("report.xml")

print("✅ Report generated: report.xml")
