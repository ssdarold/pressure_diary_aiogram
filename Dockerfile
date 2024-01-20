FROM python:3.8.10

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем код проекта в контейнер
COPY . /app/

# Запускаем Gunicorn при старте контейнера
CMD ["python", "bot-main.py"]