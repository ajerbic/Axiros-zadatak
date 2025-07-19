from flask import Flask, request, Response
from datetime import datetime
import requests

app = Flask(__name__)

SERVICE1_URL = "http://service1:8080"
VALID_FORMATS = {"iso", "epoch"}

@app.route("/", methods=["POST"])
def handle_request():
    format_type = request.get_data(as_text=True).strip().lower()

    if format_type not in VALID_FORMATS:
        return Response("Invalid format type. Use 'iso' or 'epoch'.", status=400)

    # Map epoch to timestamp for service1
    service1_format = "timestamp" if format_type == "epoch" else format_type

    try:
        # Ask Service1 for timestamp string
        response = requests.post(SERVICE1_URL, data=service1_format, timeout=3)
        response.raise_for_status()
        timestamp = response.text.strip()
    except requests.RequestException:
        return Response("Service1 is unavailable.", status=503)

    try:
        if format_type == "iso":
            # Parse ISO format timestamp and format date output
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%Y-%m-%d")
        else:  # epoch
            # Parse epoch timestamp string to int and convert to datetime
            dt = datetime.utcfromtimestamp(int(timestamp))
            return dt.strftime("%Y-%m-%d")
    except Exception as e:
        return Response(f"Invalid timestamp format from Service1: {str(e)}", status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)