web: gunicorn iexam.wsgi:application --log-file -
worker: celery -A iexam worker --loglevel=info
beat: celery -A iexam beat --loglevel=info