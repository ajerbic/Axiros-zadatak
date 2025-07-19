import requests
import subprocess
import time
import sys

SERVICE1_URL = "http://localhost:8081"
SERVICE2_URL = "http://localhost:8082"
LOG_FILE = "test_log.txt"

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

sys.stdout = Logger(LOG_FILE)

def test_service(url, input_data, description):
    try:
        print(f"\nTest: {description}")
        response = requests.post(url, data=input_data, timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text.strip()}")
        # Don't raise for status - we want to see 4xx responses
        if response.status_code >= 500:
            print(f"Server error occurred")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

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

def main():
    print("=== Valid Input Tests ===")
    # Test valid inputs first
    test_service(SERVICE1_URL, "iso", "Service1 valid input: 'iso'")
    test_service(SERVICE1_URL, "timestamp", "Service1 valid input: 'timestamp'")
    test_service(SERVICE2_URL, "iso", "Service2 valid input: 'iso'")
    test_service(SERVICE2_URL, "epoch", "Service2 valid input: 'epoch'")

    print("\n=== Input Validation Tests ===")
    invalid_inputs = ["", "foobar", "123abc", "\n", "TIMESTAMP"]
    for invalid in invalid_inputs:
        test_service(SERVICE1_URL, invalid, f"Service1 invalid input: '{repr(invalid)}'")
        test_service(SERVICE2_URL, invalid, f"Service2 invalid input: '{repr(invalid)}'")

    print("\n=== Error Handling Test: Service1 Down ===")
    stop_service("service1")
    time.sleep(2)

    test_service(SERVICE2_URL, "iso", "Service2 request when Service1 is stopped")

    # Final cleanup: stop both containers
    print("\n=== Cleaning up: Stopping all services ===")
    stop_service("service2")
    stop_service("service1")

if __name__ == "__main__":
    main()