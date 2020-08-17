release: python manage.py migrate
web: gunicorn tweet_summary.wsgi --log-file -
worker: celery -A tweet_summary worker --beat --events --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler