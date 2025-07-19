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
        # Instead of raising immediately, show status code and response text
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text.strip()}")
        response.raise_for_status()  # still raise for unexpected errors if you want
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e} - Response content: {e.response.text.strip() if e.response else 'No content'}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def stop_service(container_name):
    print(f"\nStopping container: {container_name}")
    subprocess.run(["docker", "stop", container_name], capture_output=True)

def start_service(container_name, version, port):
    print(f"\nStarting container: {container_name}")
    subprocess.run([
        "docker", "run", "-d", "--rm",
        "--name", container_name,
        "--network", "microservices-net",
        "-p", f"{port}:8080",
        f"ajerbic/{container_name}:{version}"
    ], capture_output=True)
    time.sleep(3)

def main():
    print("=== Input Validation Tests ===")
    invalid_inputs = ["", "foobar", "123abc", "\n", "TIMESTAMP"]
    for invalid in invalid_inputs:
        test_service(SERVICE1_URL, invalid, f"Service1 invalid input: '{invalid}'")
        test_service(SERVICE2_URL, invalid, f"Service2 invalid input: '{invalid}'")

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
