FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install flask flask-cors google-generativeai psycopg2-binary

CMD ["python", "app.py"]