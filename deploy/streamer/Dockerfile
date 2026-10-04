# Streamer for the streaming paper tier (issue #69, docs/streaming-design.md). Paper only.
# Build from the repo root:  docker build -f deploy/streamer/Dockerfile -t tdf-streamer .
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
COPY deploy/streamer/requirements.txt ./deploy/streamer/requirements.txt
RUN pip install --no-cache-dir -r deploy/streamer/requirements.txt
COPY factory ./factory
COPY strategies ./strategies
COPY protected ./protected
COPY state ./state
# the strategy child process runs as this user, with no credentials in its environment
RUN useradd --system --no-create-home sandbox && mkdir -p /var/log/stream
ENV FACTORY_SANDBOX_USER=sandbox STREAM_LOG_DIR=/var/log/stream PORT=8080 PYTHONUNBUFFERED=1
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,sys; sys.exit(urllib.request.urlopen('http://127.0.0.1:8080/healthz').status != 200)"
CMD ["python", "-m", "factory.stream.app"]
