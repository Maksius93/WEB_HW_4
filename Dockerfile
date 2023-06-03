# Docker-команда FROM указывает базовый образ контейнера
# Наш базовый образ - это Linux с предустановленным python-3.10
FROM python:3.11

# Установим переменную окружения
ENV WEB_HW_4 /main

# Установим рабочую директорию внутри контейнера
WORKDIR $WEB_HW_4

COPY pyproject.toml $WEB_HW_2/pyproject.toml
COPY poetry.lock $WEB_HW_2/poetry.lock

# Установим зависимости внутри контейнера
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main

# Скопируем остальные файлы в рабочую директорию контейнера
COPY . .


# Запустим наше приложение внутри контейнера
CMD ["python", "main.py"]