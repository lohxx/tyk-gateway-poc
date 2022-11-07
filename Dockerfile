FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get -qq -y install \
        libpq-dev \
        gcc \
        vim

RUN pip install poetry==1.1.14

COPY ./ /app
COPY poetry.lock /app
COPY pyproject.toml /app

WORKDIR /app/
RUN poetry config virtualenvs.create false
RUN poetry install -v

EXPOSE 8000