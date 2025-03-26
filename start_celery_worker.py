import socket
import subprocess
import os

hostname = socket.gethostname()
worker_id = os.environ.get('CELERY_WORKER_ID', '1')  # Получаем ID из переменной среды, по умолчанию '1'
nodename = f"worker-{worker_id}@{hostname}"

celery_command = [
    "celery",
    "-A",
    "celery_app.app",
    "worker",
    "-l",
    "info",
    "-E",
    "-n",
    nodename,
    "-Q",  # Добавление аргумента очереди
    "mailing_queue",  # Очередь Celery по умолчанию
]

subprocess.run(celery_command)
