# Dockerfile
FROM python:3.11-slim-bookworm

# Update system packages to address vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Генерируем protobuf файлы
RUN python generate_protos.py

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
