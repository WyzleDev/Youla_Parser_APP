FROM python:3.9.5-alpine3.13
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.6

# install curl
RUN apk add --no-cache build-base linux-headers curl \
    && rm -rf /var/cache/apk/*

## install poetry
RUN curl -sSL "https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py" | python -
RUN ln -s "${HOME}"/.poetry/bin/poetry /usr/bin/poetry && \
    poetry config virtualenvs.create false


RUN mkdir -p /usr/app/

WORKDIR /usr/app/

COPY . /usr/app/

RUN poetry install


CMD ["python3", "main.py"]