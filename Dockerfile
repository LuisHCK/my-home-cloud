FROM python:3-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_PATH /opt/app

WORKDIR $APP_PATH

COPY requirements.txt $APP_PATH

RUN pip install -r requirements.txt

COPY . $APP_PATH