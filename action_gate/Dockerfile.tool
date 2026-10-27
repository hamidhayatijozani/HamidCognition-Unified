FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser && mkdir -p /data && chown -R appuser:appuser /data
COPY tool_server.py security_authority.py ./
# Named volumes can retain root-owned files from an earlier container. Repair
# ownership before dropping privileges so the persistent nonce database remains
# writable across container recreation without running the tool as root.
CMD ["sh", "-c", "mkdir -p /data && chown -R appuser:appuser /data && exec su -s /bin/sh appuser -c 'exec python tool_server.py'"]
EXPOSE 9000
