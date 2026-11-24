# Postgres for dev and CI, with SSL turned on.
#
# Production (RDS) forces SSL, so dev and CI do too, and the app connects with
# sslmode=require everywhere. Without this, a broken SSL setup on the client
# side goes unnoticed until it reaches production. See:
# https://github.com/freelawproject/courtlistener/issues/2827
#
# The certificate is self-signed and generated when the image is built, so no
# private key is committed to the repo. It is only good for encrypting the
# connection; nothing verifies it, so never use this image in production.
ARG POSTGRES_VERSION=18.6-alpine
FROM postgres:${POSTGRES_VERSION}

RUN apk add --no-cache openssl \
    && mkdir -p /etc/ssl/private \
    && openssl req -new -x509 -nodes -days 36500 \
        -subj "/CN=bc2-postgresql" \
        -keyout /etc/ssl/private/bc2-postgres.key \
        -out /etc/ssl/private/bc2-postgres.crt \
    && chown -R postgres:postgres /etc/ssl/private \
    && chmod 0700 /etc/ssl/private \
    && chmod 0600 /etc/ssl/private/bc2-postgres.*

COPY pg_hba.conf /etc/postgresql/pg_hba.conf

CMD ["postgres", \
     "-c", "ssl=on", \
     "-c", "ssl_cert_file=/etc/ssl/private/bc2-postgres.crt", \
     "-c", "ssl_key_file=/etc/ssl/private/bc2-postgres.key", \
     "-c", "hba_file=/etc/postgresql/pg_hba.conf"]
