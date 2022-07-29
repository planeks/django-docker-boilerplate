FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED 1

# Remove adding NodeJS repository if you do not need it
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
  && apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # Some extra packages
  && apt-get install -y curl nano graphviz \
  # Other dependencies \
  # Remove the next line if you do not need NodeJS
  && apt-get install -y nodejs \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN addgroup --gid 1024 appuser \
    && adduser --disabled-password --gecos "" --force-badname --ingroup appuser appuser

# Requirements are installed here to ensure they will be cached.
COPY ./src/requirements.txt /requirements.txt
RUN pip install -U pip pip-tools && pip install --no-cache-dir -r /requirements.txt && rm -rf /requirements.txt

COPY --chown=appuser:appuser ./docker/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

# We use the directory /opt/project/src for PyCharm compatibility
COPY --chown=appuser:appuser ./src /opt/project/src

RUN mkdir /data
RUN chown -R appuser:appuser /data
RUN chmod 775 /data
RUN chmod g+s /data

USER appuser

WORKDIR /opt/project/src

ENTRYPOINT ["/entrypoint"]
