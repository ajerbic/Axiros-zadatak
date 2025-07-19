import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import requests
from datetime import datetime

SERVICE1_URL = "http://service1:8080"
VALID_FORMATS = {"iso", "epoch"}

def main():
    # Read input from stdin (this is how fwatchdog passes data)
    input_data = sys.stdin.read().strip().lower()
    
    # Validate format
    if input_data not in VALID_FORMATS:
        print("Invalid format type. Use 'iso' or 'epoch'.")
        sys.exit(1)
    
    # Map epoch to timestamp for service1
    service1_format = "timestamp" if input_data == "epoch" else input_data
    
    try:
        # Ask Service1 for timestamp string
        response = requests.post(SERVICE1_URL, data=service1_format, timeout=3)
        response.raise_for_status()
        timestamp = response.text.strip()
    except requests.RequestException as e:
        print("Service1 is unavailable.")
        sys.exit(1)
    
    try:
        if input_data == "iso":
            # Parse ISO format timestamp and format date output
            dt = datetime.fromisoformat(timestamp)
            print(dt.strftime("%Y-%m-%d"))
        else:  # epoch
            # Parse epoch timestamp string to int and convert to datetime
            dt = datetime.utcfromtimestamp(int(timestamp))
            print(dt.strftime("%Y-%m-%d"))
    except Exception as e:
        print(f"Invalid timestamp format from Service1: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()