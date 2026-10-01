FROM python:3.12-slim
WORKDIR /app
COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dashboard/app.py .
COPY dashboard/static ./static
RUN useradd --create-home --uid 10002 appuser
USER appuser
EXPOSE 8081
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8081"]
