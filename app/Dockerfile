# 1. Menggunakan base image Python resmi yang ringan (slim)
FROM python:3.10-slim

# 2. Menentukan working directory di dalam container
WORKDIR /app

# 3. Install system dependencies yang dibutuhkan oleh driver MySQL (mencegah error build)
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Menyalin requirements.txt terlebih dahulu untuk memanfaatkan cache Docker
COPY requirements.txt .

# 5. Menginstal semua dependencies Python tanpa menyimpan cache installer
RUN pip install --no-cache-dir -r requirements.txt

# 6. Menyalin seluruh source code Flask ke dalam container
COPY . .

# 7. Menginformasikan bahwa container ini akan berjalan di port 80 (disesuaikan dengan ecs.tf)
EXPOSE 80

# 8. Menjalankan Flask menggunakan Gunicorn di port 80
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]