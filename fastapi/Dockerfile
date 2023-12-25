FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .

# необходимо для установки psycopg2 без ошибок
RUN apt-get update && apt-get -y install libpq-dev gcc 

RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN ["chmod", "777", "/app/scripts.sh"]
ENTRYPOINT ["/app/scripts.sh"]
