FROM python:3.12-bullseye

ENV PYTHONUNBUFFERED 1

RUN pip install mkdocs mkdocs-material mkdocstrings[crystal,python] mkdocs-awesome-pages-plugin mkdocs-graphviz

COPY ./docker/mkdocs/mkdocs.yml /mkdocs.yml

RUN mkdir /docs
COPY ./docs /docs

RUN mkdir /data

EXPOSE 8000
CMD ["mkdocs", "serve", "-f", "/mkdocs.yml", "-a", "0.0.0.0:8000"]
