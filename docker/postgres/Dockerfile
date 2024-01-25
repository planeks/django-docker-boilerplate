FROM postgres:16

# Uncomment the next line if you need to host multiple databases per cluster
# COPY ./docker/postgres/create_multiple_databases.sh /docker-entrypoint-initdb.d

COPY ./docker/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance
