web: gunicorn -k uvicorn.workers.UvicornWorker config.asgi:application --bind 0.0.0.0:$PORT
worker: celery -A config worker -l info
beat: celery -A config beat -l info
