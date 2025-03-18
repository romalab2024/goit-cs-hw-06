import socket
import json
from datetime import datetime
from pymongo import MongoClient

# Підключення до MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["chat_database"]
collection = db["messages"]

# Налаштування сервера
HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 1024

# Створюємо TCP-сервер
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print(f"Socket-сервер запущено на {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    print(f"Отримано з'єднання від {addr}")

    data = conn.recv(BUFFER_SIZE).decode("utf-8")
    if not data:
        continue

    try:
        message_data = json.loads(data)
        message_data["date"] = str(datetime.now())

        # Збереження у MongoDB
        collection.insert_one(message_data)
        print("Дані збережено:", message_data)

        conn.sendall(b"Message received")
    except Exception as e:
        print("Помилка:", e)
        conn.sendall(b"Error processing message")

    conn.close()
