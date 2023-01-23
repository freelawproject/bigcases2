ARG BUILD_ENV=prod

FROM python:3.10-slim as build-base

RUN apt-get update --option "Acquire::Retries=3" --quiet=2 && \
    apt-get install \
        --no-install-recommends \
        --assume-yes \
        --quiet=2 \
        # So we can use Python-slim
        build-essential gcc python3-dev\
        # So postgres can compile and users can use dbshell
        libpq-dev postgresql-client \
        # For installing poetry and git-based deps
        curl git \
        # Other dependencies
        libffi-dev libxml2-dev libxslt-dev procps vim cmake

# poetry
# https://python-poetry.org/docs/configuration/#using-environment-variables
ENV POETRY_VERSION=1.3.2 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # Don't build a virtualenv to save space
    POETRY_VIRTUALENVS_CREATE=false \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

ARG POETRY_HOME

ENV PYTHONUNBUFFERED=1 \
    # paths
    # where to create the env
    VENV_PATH="/opt/pysetup/.venv" \
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup"

# prepend poetry and venv to path
ENV PATH="/opt/poetry/bin:$VENV_PATH/bin:$PATH"


FROM build-base as build-dev

WORKDIR $PYSETUP_PATH

COPY poetry.lock ./
COPY pyproject.toml ./
RUN poetry install

COPY . /opt/bigcases2

CMD python /opt/bigcases2/manage.py migrate  && \
    python /opt/bigcases2/manage.py runserver 0.0.0.0:8000


