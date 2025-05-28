ARG BUILD_ENV=prod

FROM python:3.11 as build-base

# Install uv
# https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/

# Install apt dependencies
# caching: https://docs.docker.com/build/cache/optimize/#use-cache-mounts
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update --option "Acquire::Retries=3" --quiet=2 && \
    curl -sL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install \
        --no-install-recommends \
        --assume-yes \
        --quiet=2 \
        # So we can use django-tailwind
        nodejs \
        # So postgres can compile and users can use dbshell
        libpq-dev postgresql-client \
        # For installing Git-based deps
        git

# set environment variables
ENV PYTHONUNBUFFERED=1

ARG BUILD_ENV=prod
FROM build-base as python-base

WORKDIR /opt/bigcases2

# We log to stdout by default, but we have a config for logging here. Even if
# we don't use this logger, we need to have the file or else Python is unhappy.
RUN mkdir /var/log/bigcases2 \
  && chown -R www-data:www-data /var/log/bigcases2

# Install Python dependencies
COPY pyproject.toml uv.lock ./
# https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/venv \
    PATH="/venv/bin:$PATH"
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

COPY . .

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
