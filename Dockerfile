FROM python:3.7-slim

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN useradd api-managment
RUN chown -R api-managment:api-managment /app
USER api-managment