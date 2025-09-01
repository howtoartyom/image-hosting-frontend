import http.server
import re
import logging
import json
import os
from urllib.parse import urlparse
import uuid

STATIC_FILES_DIR = 'static'
UPLOAD_DIR = 'images'
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
log_dir = 'logs'

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log')),
        logging.StreamHandler()
    ]
)


class ImageHostingHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='text/html'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def _get_content_type(self, file_path):
        if file_path.endswith('.html'):
            return 'text/html'
        elif file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.js'):
            return 'application/javascript'
        elif file_path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return 'image/' + file_path.split('.')[-1]
        else:
            return 'application/octet-stream'

    def do_GET(self):
        logging.warning(f"Действие: Неожиданный GET запрос: {self.path}. Возможно, Nginx не настроен корректно или это ошибка клиента.")
        self._set_headers(404, 'text/plain')
        self.wfile.write(b"404 Not Found (Handled by Nginx for static files, or unexpected backend request)")


    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/upload':
            # 1. Получаем заголовок Content-Type
            content_type_header = self.headers.get('Content-Type')
            if not content_type_header or not content_type_header.startswith('multipart/form-data'):
                logging.warning("Действие: Ошибка загрузки - некорректный Content-Type.")
                self._set_headers(400, 'application/json')
                response = {"status": "error", "message": "Ожидается multipart/form-data."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            # 2. Извлекаем boundary из Content-Type
            try:
                boundary = content_type_header.split('boundary=')[1].encode('utf-8')
            except IndexError:
                logging.warning("Действие: Ошибка загрузки - boundary не найден в Content-Type.")
                self._set_headers(400, 'application/json')
                response = {"status": "error", "message": "Boundary не найден."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            # 3. Читаем тело запроса
            try:
                content_length = int(self.headers['Content-Length'])
                if content_length > MAX_FILE_SIZE * 2:  # Небольшой запас на служебную информацию multipart
                    logging.warning(
                        f"Действие: Ошибка загрузки - запрос превышает максимальный размер ({content_length} байт).")
                    self._set_headers(413, 'application/json')  # Payload Too Large
                    response = {"status": "error", "message": f"Запрос слишком большой."}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return

                raw_body = self.rfile.read(content_length)
            except (TypeError, ValueError):
                logging.error("Ошибка: Некорректный Content-Length.")
                self._set_headers(411, 'application/json')  # Length Required
                response = {"status": "error", "message": "Некорректный Content-Length."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            except Exception as e:
                logging.error(f"Ошибка при чтении тела запроса: {e}")
                self._set_headers(500, 'application/json')
                response = {"status": "error", "message": "Ошибка при чтении запроса."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            # 4. Парсим multipart/form-data (упрощенно, только для одного файла)
            parts = raw_body.split(b'--' + boundary)
            file_data = None
            filename = None

            for part in parts:
                if b'Content-Disposition: form-data;' in part and b'filename=' in part:
                    try:
                        headers_end = part.find(b'\r\n\r\n')
                        headers_str = part[0:headers_end].decode('utf-8')

                        # Извлекаем имя файла
                        filename_match = re.search(r'filename="([^"]+)"', headers_str)
                        if filename_match:
                            filename = filename_match.group(1)

                        # Извлекаем данные файла
                        file_data = part[headers_end + 4:].strip()  # +4 для \r\n\r\n
                        break
                    except Exception as e:
                        logging.error(f"Ошибка при парсинге части multipart: {e}")
                        continue

            if not file_data or not filename:
                logging.warning(f"Действие: Ошибка загрузки - файл не найден в multipart-запросе.")
                self._set_headers(400, 'application/json')
                response = {"status": "error", "message": "Файл не найден в запросе."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            # Теперь у нас есть filename (строка) и file_data (bytes)
            # 5. Проверки файла
            file_size = len(file_data)
            file_extension = os.path.splitext(filename)[1].lower()

            if file_extension not in ALLOWED_EXTENSIONS:
                logging.warning(f"Действие: Ошибка загрузки - неподдерживаемый формат файла ({filename})")
                self._set_headers(400, 'application/json')
                response = {"status": "error",
                            "message": f"Неподдерживаемый формат файла. Допустимы: {', '.join(ALLOWED_EXTENSIONS)}"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            if file_size > MAX_FILE_SIZE:
                logging.warning(
                    f"Действие: Ошибка загрузки - файл превышает максимальный размер ({filename}, {file_size} байт)")
                self._set_headers(400, 'application/json')
                response = {"status": "error",
                            "message": f"Файл превышает максимальный размер {MAX_FILE_SIZE / (1024 * 1024):.0f}MB."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            # 6. Сохранение файла
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            target_path = os.path.join(UPLOAD_DIR, unique_filename)

            try:
                with open(target_path, 'wb') as f:
                    f.write(file_data)

                file_url = f"/images/{unique_filename}"
                logging.info(
                    f"Действие: Изображение '{filename}' (сохранено как '{unique_filename}') успешно загружено. Ссылка: {file_url}")
                self._set_headers(200, 'application/json')
                response = {
                    "status": "success",
                    "message": "Файл успешно загружен.",
                    "filename": unique_filename,
                    "url": file_url
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))

            except Exception as e:
                logging.error(f"Ошибка при сохранении файла '{filename}' в '{target_path}': {e}")
                self._set_headers(500, 'application/json')
                response = {"status": "error", "message": "Произошла ошибка при сохранении файла."}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            # Если POST запрос пришел не на /upload, то это неизвестный путь
            logging.warning(f"Действие: Неизвестный POST запрос на: {self.path}")
            self._set_headers(404, 'text/plain')
            self.wfile.write(b"404 Not Found")


def run_server(server_class=http.server.HTTPServer, handler_class=ImageHostingHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Сервер запущен на порту {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Сервер остановлен.")


if __name__ == '__main__':
    run_server()
