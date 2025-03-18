import http.server
import socketserver
import os
import json
import socket
from pymongo import MongoClient
import datetime

# Налаштування серверів
PORT = 3000
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 5000
BASE_DIR = "/app"
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# **Підключення до MongoDB**
MONGO_URI = "mongodb://mongo:27017/"
client = MongoClient(MONGO_URI)
db = client["chat_database"]
collection = db["messages"]

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            file_path = os.path.join(TEMPLATES_DIR, "index.html")
        elif self.path == "/message.html":
            file_path = os.path.join(TEMPLATES_DIR, "message.html")
        elif self.path.startswith("/static/"):
            file_path = os.path.join(STATIC_DIR, self.path.lstrip("/static/"))
        else:
            file_path = os.path.join(TEMPLATES_DIR, "error.html")

        if os.path.exists(file_path):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(os.path.join(TEMPLATES_DIR, "error.html"), "rb") as f:
                self.wfile.write(f.read())

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")

            data_dict = dict(x.split("=") for x in post_data.split("&"))
            username = data_dict.get("username", "Unknown")
            message = data_dict.get("message", "")

            # **Збереження в MongoDB**
            new_message = {
                "username": username,
                "message": message,
                "date": datetime.datetime.now().isoformat()
            }
            collection.insert_one(new_message)
            print("Дані збережено:", new_message)

            # **Відправка на сокет-сервер**
            from bson import json_util
            data_json = json_util.dumps(new_message)

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SOCKET_HOST, SOCKET_PORT))
                sock.sendall(data_json.encode("utf-8"))
                response = sock.recv(1024).decode("utf-8")
                sock.close()
                print("Відповідь від сокет-сервера:", response)
            except Exception as e:
                print("Помилка сокет-з'єднання:", e)

            self.send_response(302)
            self.send_header("Location", "/message.html")
            self.end_headers()

# Запуск сервера
with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
    print(f"HTTP-сервер запущено на порту {PORT}")
    httpd.serve_forever()
