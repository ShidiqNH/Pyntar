# 1. Menggunakan base image Python resmi yang ringan (slim)
FROM python:3.10-slim

# 2. Menentukan working directory di dalam container
WORKDIR /app

# 3. Menyalin requirements.txt terlebih dahulu untuk memanfaatkan cache Docker
COPY requirements.txt .

# 4. Menginstal semua dependencies Python tanpa menyimpan cache installer (biar image kecil)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Menyalin seluruh source code Flask dari laptop ke dalam container
COPY . .

# 6. Menginformasikan bahwa container ini akan berjalan di port 8000
EXPOSE 8000

# 7. Menjalankan Flask menggunakan Gunicorn (WSGI Server untuk Production)
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]