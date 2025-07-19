import requests
import subprocess
import time
import sys
import re

SERVICE1_URL = "http://localhost:8081"
SERVICE2_URL = "http://localhost:8082"
LOG_FILE = "test_log.txt"
RESULTS_FILE = "test_results.txt"

# Logger: write to both terminal and log file
class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.logfile = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.logfile.write(message)

    def flush(self):
        self.terminal.flush()
        self.logfile.flush()

# Results tracker
class ResultsTracker:
    def __init__(self, filename):
        self.results_file = open(filename, "w", encoding="utf-8")
        self.results_file.write("# Test Results: 1 = Pass, 0 = Fail\n")

    def record_result(self, test_name, passed):
        result = 1 if passed else 0
        self.results_file.write(f"{test_name}: {result}\n")
        self.results_file.flush()

    def close(self):
        self.results_file.close()

sys.stdout = Logger(LOG_FILE)
results = ResultsTracker(RESULTS_FILE)

def test_service(url, input_data, description, expected_status=200, expected_content_check=None):
    """
    Test a service and return whether it passed expectations
    expected_content_check: function that takes response text and returns True/False
    """
    try:
        print(f"\nTest: {description}")
        response = requests.post(url, data=input_data, timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text.strip()}")
        
        # Check status code
        status_ok = response.status_code == expected_status
        
        # Check content if checker function provided
        content_ok = True
        if expected_content_check:
            content_ok = expected_content_check(response.text.strip())
        
        passed = status_ok and content_ok
        if not passed:
            print(f"FAIL: Expected status {expected_status}, got {response.status_code}")
            if expected_content_check and not content_ok:
                print(f"FAIL: Content check failed")
        else:
            print("PASS")
            
        return passed
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        print("FAIL")
        return False

def stop_service(container_name):
    print(f"\nStopping container: {container_name}")
    result = subprocess.run(["docker", "stop", container_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Warning: Failed to stop {container_name} - it may not be running")

def start_service(container_name, version, port):
    print(f"\nStarting container: {container_name}")
    result = subprocess.run([
        "docker", "run", "-d", "--rm",
        "--name", container_name,
        "--network", "microservices-net",
        "-p", f"{port}:8080",
        f"ajerbic/{container_name}:{version}"
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error starting container: {result.stderr}")
    time.sleep(3)

def is_iso_timestamp(text):
    """Check if text looks like an ISO timestamp"""
    iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+$'
    return bool(re.match(iso_pattern, text))

def is_epoch_timestamp(text):
    """Check if text looks like an epoch timestamp (10 digits)"""
    return text.isdigit() and len(text) == 10

def is_date_format(text):
    """Check if text looks like YYYY-MM-DD"""
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(date_pattern, text))

def contains_error_message(expected_message):
    """Returns a function that checks if response contains expected error message"""
    def checker(text):
        return expected_message in text
    return checker

def main():
    print("=== Valid Input Tests ===")
    
    # Service1 valid tests
    test_name = "service1_iso_valid"
    passed = test_service(SERVICE1_URL, "iso", "Service1 valid input: 'iso'", 
                         expected_status=200, expected_content_check=is_iso_timestamp)
    results.record_result(test_name, passed)
    
    test_name = "service1_timestamp_valid"
    passed = test_service(SERVICE1_URL, "timestamp", "Service1 valid input: 'timestamp'",
                         expected_status=200, expected_content_check=is_epoch_timestamp)
    results.record_result(test_name, passed)
    
    # Service2 valid tests
    test_name = "service2_iso_valid"
    passed = test_service(SERVICE2_URL, "iso", "Service2 valid input: 'iso'",
                         expected_status=200, expected_content_check=is_date_format)
    results.record_result(test_name, passed)
    
    test_name = "service2_epoch_valid"
    passed = test_service(SERVICE2_URL, "epoch", "Service2 valid input: 'epoch'",
                         expected_status=200, expected_content_check=is_date_format)
    results.record_result(test_name, passed)

    print("\n=== Input Validation Tests ===")
    
    # Invalid inputs for Service1 (should default to ISO format)
    invalid_inputs = ["", "foobar", "123abc", "\n", "TIMESTAMP"]
    for i, invalid in enumerate(invalid_inputs):
        test_name = f"service1_invalid_{i+1}"
        passed = test_service(SERVICE1_URL, invalid, f"Service1 invalid input: '{repr(invalid)}'",
                             expected_status=200, expected_content_check=is_iso_timestamp)
        results.record_result(test_name, passed)
    
    # Invalid inputs for Service2 (should return 500 with error message)
    for i, invalid in enumerate(invalid_inputs):
        test_name = f"service2_invalid_{i+1}"
        passed = test_service(SERVICE2_URL, invalid, f"Service2 invalid input: '{repr(invalid)}'",
                             expected_status=500, 
                             expected_content_check=contains_error_message("Invalid format type"))
        results.record_result(test_name, passed)

    print("\n=== Error Handling Test: Service1 Down ===")
    stop_service("service1")
    time.sleep(2)

    test_name = "service2_service1_down"
    passed = test_service(SERVICE2_URL, "iso", "Service2 request when Service1 is stopped",
                         expected_status=500,
                         expected_content_check=contains_error_message("Service1 is unavailable"))
    results.record_result(test_name, passed)

    # Final cleanup: stop both containers
    print("\n=== Cleaning up: Stopping all services ===")
    stop_service("service2")
    
    # Close results file
    results.close()
    print(f"\nTest results saved to: {RESULTS_FILE}")

if __name__ == "__main__":
    main()