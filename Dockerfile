FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Install dependensi sistem yang dibutuhkan untuk mysql-connector/cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copas requirements dari folder app lokal ke container
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copas seluruh isi folder app lokal ke dalam working directory container
COPY app/ .

# Ekspos port 8000 sesuai dengan target group ECS dan ALB
EXPOSE 8000

# Perintah produksi menggunakan Gunicorn (Membuka port 8000 dengan nama modul 'app' dan instance 'app')
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]