FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py storage.py rate_limit.py ./
RUN mkdir -p /data
ENV ACTION_GATE_DB=/data/action_gate.db
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()"
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
