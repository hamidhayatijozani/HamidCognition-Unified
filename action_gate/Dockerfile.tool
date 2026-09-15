FROM python:3.12-slim
WORKDIR /app
COPY tool_server.py .
EXPOSE 9000
CMD ["python", "tool_server.py"]
