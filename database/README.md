# Docker image for Postgres database

Don't use this in production.

## Build container

```shell
docker build -t bigcases2-db ./
```

## Run container

```shell
docker run -d --name bigcases2-db -p 5432:5432 bigcases2-db
```
