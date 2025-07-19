FROM python:3.12-slim

# Install curl and download the latest classic watchdog binary from GitHub releases
RUN apt-get update && apt-get install -y curl --no-install-recommends && \
    curl -sL https://github.com/openfaas/classic-watchdog/releases/latest/download/fwatchdog-amd64 -o /usr/bin/fwatchdog && \
    chmod +x /usr/bin/fwatchdog && \
    apt-get purge -y --auto-remove curl && \
    rm -rf /var/lib/apt/lists/*


ENV fprocess="python /entrypoint.py"

COPY entrypoint.py /

EXPOSE 8080

CMD ["fwatchdog"]
