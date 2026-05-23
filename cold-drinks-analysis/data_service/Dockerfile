FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir flask pandas
COPY . .
EXPOSE 5001
CMD ["python", "app.py"]
