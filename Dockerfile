FROM python:3.9-slim

WORKDIR /usr/src/app

RUN apt update && \
    apt install -y build-essential libpq-dev

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./app.py"]
