# https://dev.to/andre347/how-to-easily-create-a-postgres-database-in-docker-4moj
FROM postgres
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB bigcases2
COPY schema.sql /docker-entrypoint-initdb.d/
