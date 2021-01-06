# Django Docker Boilerplate from PLANEKS

## How to create the project

```shell
$ python3 -m venv venv
$ source venv/bin/activate
$ wget https://github.com/planeks/django-docker-boilerplate/archive/0.9.tar.gz
$ django-admin startproject myproject --template 0.9.tar.gz -e py,html,md,yml -n start
```

After successful project creation you may delete `venv` directory and downloaded
archive.

## Running the project on locale machine

During development, you need to run the project locally. First, of all, copy
the file `local.env` to the file `.env` in the same directory.

```shell
$ cp local.env .env
```

Open the `.env` file in your editor and specify the settings:

```shell
PYTHONENCODING=utf8
DEBUG=1
CONFIGURATION=dev
DJANGO_LOG_LEVEL=INFO
SECRET_KEY="<secret_key>"
SQLITE_DB=/extras/myproject.sqlite3
REDIS_URL=redis://redis:6379/0
STATIC_ROOT=/staticfiles
SESSION_FILE_PATH=/sessions
EMAIL_FILE_PATH=/email
SITE_URL=http://myproject.local:8000
```

We are atrongly recommend to create some local domain in your `/etc/hosts` file
for working with the project:

```
127.0.0.1   myproject.local
```

Also, in this template we are using SQLite for development process. If you will add
the `SQLITE_DB` variable specify the full path to the database file in the container.
In this particular case use the path like `/extras/database_file_name.db`.

We specifying the next volumes in the application container:

- `/extras` -> `data/local_extras`
- `/staticfiles` -> `data/local_staticfiles`
- `/email` -> `data/local_email`
- `/sessions` -> `data/local_sessions`

If you need to add any other directories to the container and define them as
volumes you need to edit `Dockerfile` and `local.yml` file.

Use the next command for building the containers:

```shell
$ docker-compose -f local.yml build
```

For running the project in detached mode use the next command:

```shell
$ docker-compose -f local.yml up -d
```

For running a management command like Django interactive shell, for example, you
can use the next command for running `bash` inside the container:

```shell
$ docker-compose -f local.yml exec django bash
```


