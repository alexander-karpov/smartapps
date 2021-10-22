# syntax=docker/dockerfile:1
FROM pytorch/pytorch:latest

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN mkdir -p /usr/local/share/ca-certificates/Yandex
COPY YandexInternalRootCA.crt /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt


COPY ./src .

EXPOSE 5000

RUN pip install -r requirements.txt

CMD ["python3", "app.py"]
