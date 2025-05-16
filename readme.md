
starts the asgi
uvicorn chatten.asgi:application --host 0.0.0.0 --port 8001


starts the celery worker

celery -A chatten worker --loglevel=info

starts the server

python manage.py runserver
