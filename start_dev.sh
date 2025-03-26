#!/bin/bash
export DJANGO_SETTINGS_MODULE=config.settings

# Активируем виртуальное окружение
    source .venv/bin/activate

# Запускаем redis-server (если он еще не запущен)
if ! pgrep -x "redis-server" > /dev/null
then
    redis-server &
fi

# Запускаем Celery worker
python3 start_celery_worker.py &

# Запускаем Celery beat
celery -A celery_app.app beat -l info &


# Запускаем Django runserver
python3 manage.py runserver