#!/bin/sh

sleep 2

python /code/manage.py collectstatic --noinput
# python /code/manage.py runserver 0.0.0.0:8000
cd code
chmod -R a+x static
chmod -R a+x media
uvicorn d_post.asgi:application --reload --host 0.0.0.0 --port 8080
exec "$@"