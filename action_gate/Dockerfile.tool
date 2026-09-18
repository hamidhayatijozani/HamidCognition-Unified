FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
COPY tool_server.py .
USER appuser
EXPOSE 9000
CMD ["python", "tool_server.py"]
