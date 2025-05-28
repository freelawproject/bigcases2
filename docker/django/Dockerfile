ARG BUILD_ENV=prod

FROM python:3.11-slim as build-base

# Install apt dependencies
# caching: https://docs.docker.com/build/cache/optimize/#use-cache-mounts
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update --option "Acquire::Retries=3" --quiet=2 && \
    apt-get install -y build-essential curl &&\
    curl -sL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install \
        --no-install-recommends \
        --assume-yes \
        --quiet=2 \
        # So we can use django-tailwind
        nodejs \
        # So we can use Python-slim
        gcc python3-dev \
        # So postgres can compile and users can use dbshell
        libpq-dev postgresql-client \
        # For installing poetry and git-based deps
        curl git

# poetry
# https://python-poetry.org/docs/configuration/#using-environment-variables
ENV POETRY_VERSION=2.0.0 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # Don't build a virtualenv to save space
    POETRY_VIRTUALENVS_CREATE=false \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1

ENV PYTHONUNBUFFERED=1 \
    # this is where our requirements are copied to
    PYSETUP_PATH="/opt/pysetup"

RUN python -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install poetry==$POETRY_VERSION --quiet --upgrade && \
    ln -s $POETRY_HOME/bin/poetry "$(dirname $(which python))/poetry"  # make accessible via $PATH


ARG BUILD_ENV=prod
FROM build-base as python-base

WORKDIR $PYSETUP_PATH

COPY poetry.lock pyproject.toml ./
RUN poetry install $(test "$BUILD_ENV" != "dev" && echo "--without dev")

COPY . /opt/bigcases2

WORKDIR /opt

# We log to stdout by default, but we have a config for logging here. Even if
# we don't use this logger, we need to have the file or else Python is unhappy.
RUN mkdir /var/log/bigcases2 \
  && chown -R www-data:www-data /var/log/bigcases2

WORKDIR /opt/bigcases2

# freelawproject/bigcases2:latest-rq
FROM python-base as rq

CMD python manage.py rqworker --with-scheduler

# freelawproject/bigcases2:latest-tailwind-reload-dev
FROM python-base as tailwind-reload-dev

CMD python /opt/bigcases2/manage.py tailwind install --no-input  && \
    python /opt/bigcases2/manage.py tailwind start --no-input

#freelawproject/bigcases2:latest-web-dev
FROM python-base as web-dev

CMD python /opt/bigcases2/manage.py migrate  && \
    python /opt/bigcases2/manage.py runserver 0.0.0.0:8000

WORKDIR /opt/bigcases2

#freelawproject/bigcases2:latest-web-prod
FROM python-base as web-prod

CMD python /opt/bigcases2/manage.py migrate && \
    gunicorn wsgi:application \
    --chdir /opt/bigcases2/docker/django/wsgi-configs/ \
    --user www-data \
    --group www-data \
    # Set high number of workers. Docs recommend 2-4× core count`
    --workers ${NUM_WORKERS:-16} \
    # Reset each worker once in a while
    --max-requests 10000 \
    --max-requests-jitter 100 \
    --timeout 180 \
    --bind 0.0.0.0:8888
