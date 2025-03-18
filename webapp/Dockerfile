# Використовуємо офіційний образ Python
FROM python:3.9

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо ВСІ файли з проєкту
COPY . /app

# Встановлюємо залежності
RUN pip install pymongo

# Відкриваємо порти
EXPOSE 3000 5000

# Запускаємо сервер
CMD python main.py & python socket_server.py
