FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini sources.yaml ./
COPY scripts ./scripts

COPY docker-entrypoint.sh ./
# Редакторы на Windows сохраняют скрипт с CRLF. Тогда возврат каретки попадает в
# shebang, ядро ищет интерпретатор с CR на конце имени и контейнер падает с
# No such file or directory. Срезаем CR на сборке, чтобы запуск не зависел от
# того, чем правили файл на хосте.
RUN tr -d '\r' < docker-entrypoint.sh > /tmp/entrypoint \
    && mv /tmp/entrypoint docker-entrypoint.sh \
    && chmod +x docker-entrypoint.sh

# Роль процесса выбирается переменной ROLE: api (по умолчанию) или worker.
CMD ["./docker-entrypoint.sh"]
