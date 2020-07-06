web: gunicorn tweet_summary.wsgi --log-file -
worker: celery -A tweet_summary worker --beat -loglevel info