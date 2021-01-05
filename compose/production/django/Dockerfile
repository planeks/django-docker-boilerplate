FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # Some extra packages
  && apt-get install -y curl mc nano \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN addgroup --gid 1024 django \
    && adduser --disabled-password --gecos "" --force-badname --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt && rm -rf /requirements.txt

COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY --chown=django:django ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY --chown=django:django ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

COPY --chown=django:django . /app

RUN mkdir /staticfiles
RUN chown -R django:django /staticfiles
RUN chmod 775 /staticfiles
RUN chmod g+s /staticfiles
RUN mkdir /sessions
RUN chown -R django:django /sessions
RUN chmod 775 /sessions
RUN chmod g+s /sessions
RUN mkdir /extras
RUN chown -R django:django /extras
RUN chmod 775 /extras
RUN chmod g+s /extras

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
