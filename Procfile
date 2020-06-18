web: gunicorn tweet_summary.wsgi --log-file -
worker: celery -A tweet_summary worker -events -loglevel info
beat: celery -A tweet_summary beat