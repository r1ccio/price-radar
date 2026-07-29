FROM python:3.12-slim-bookworm

ENV PYTHONDONTWITEBYTECODE 1\
    PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \ 
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* 

WORKDIR /usr/src/app

COPY requirements.txt . 
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .