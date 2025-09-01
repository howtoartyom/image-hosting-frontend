FROM python:3.10-slim AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Этап выполнения (Run Stage)
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только установленные зависимости из builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Копируем скрипт приложения
COPY app.py .

# Копируем всю директорию static
COPY static/ ./static/

# Открываем порт, который будет слушать наше приложение
EXPOSE 8000

# Команда для запуска приложения
CMD ["python", "app.py"]