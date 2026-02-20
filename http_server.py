import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

TASKS_FILE = 'tasks.txt'


class TaskStorage:
    '''Класс для хранения и управления задачами'''

    def __init__(self, filename):
        self.filename = filename
        self.tasks = []
        self.next_id = 1
        self.load()

    def load(self):
        '''Загружает задачи из файла'''
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.tasks = json.load(f)
            if self.tasks:
                self.next_id = max(task['id'] for task in self.tasks) + 1
            else:
                self.next_id = 1
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = []
            self.next_id = 1

    def save(self):
        '''Сохраняет задачи в файл'''
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def get_all(self):
        '''Возвращает список всех задач'''
        return self.tasks

    def find_task_id(self, task_id):
        '''Ищет задачу по id'''
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None

    def add_task(self, title, priority):
        '''Добавляет новую задачу'''
        task = {
            'id': self.next_id,
            'title': title,
            'priority': priority,
            'isDone': False
        }
        self.tasks.append(task)
        self.next_id += 1
        self.save()
        return task

    def complete_task(self, task_id):
        '''Отмечает задачу выполненной'''
        task = self.find_task_id(task_id)
        if task:
            task['isDone'] = True
            self.save()
            return True
        return False


class TaskHTTPHandler(BaseHTTPRequestHandler):
    '''Обработчик HTTP-запросов'''

    storage = None

    def send_json(self, data, status=200):
        '''Отправляет JSON-ответ'''
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if data is not None:
            json_str = json.dumps(data, ensure_ascii=False)
            self.wfile.write(json_str.encode('utf-8'))
            self.wfile.flush()

    def send_error_message(self, status, message):
        '''Отправляет ответ с ошибкой'''
        self.send_json({'error': message}, status)

    def do_GET(self):
        '''Обрабатывает GET-запросы'''
        parsed = urlparse(self.path)
        if parsed.path == '/tasks':
            self.handle_get_tasks()
        else:
            self.send_error_message(404, 'Not found')

    def handle_get_tasks(self):
        '''Обрабатывает GET /tasks'''
        tasks = self.storage.get_all()
        self.send_json(tasks)

    def do_POST(self):
        '''Обрабатывает POST-запросы'''
        parsed = urlparse(self.path)
        if parsed.path == '/tasks':
            self.handle_post_tasks()
        else:
            match = re.search(r'^/tasks/(\d+)/complete$', parsed.path)
            if match:
                task_id = int(match.group(1))
                self.handle_post_complete(task_id)
            else:
                self.send_error_message(404, 'Not found')

    def handle_post_tasks(self):
        '''Обрабатывает POST /tasks (создание задачи)'''
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error_message(400, 'Empty request body')
            return

        post_data = self.rfile.read(content_length)

        # Пробуем декодировать UTF-8, если не получается — пробуем cp1251
        try:
            decoded_str = post_data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                decoded_str = post_data.decode('cp1251')
            except UnicodeDecodeError:
                self.send_error_message(400, 'Invalid encoding. Use UTF-8 or CP1251.')
                return

        try:
            data = json.loads(decoded_str)
        except json.JSONDecodeError:
            self.send_error_message(400, 'Invalid JSON')
            return

        if 'title' not in data or 'priority' not in data:
            self.send_error_message(400, 'Missing required fields: title and priority')
            return

        priority = data['priority']
        if priority not in ['low', 'normal', 'high']:
            self.send_error_message(400, 'Priority must be one of: low, normal, high')
            return

        try:
            new_task = self.storage.add_task(data['title'], priority)
        except Exception as e:
            print(f"Ошибка сохранения задачи: {e}")
            self.send_error_message(500, 'Internal server error: unable to save task')
            return

        self.send_json(new_task, 201)

    def handle_post_complete(self, task_id):
        '''Обрабатывает POST /tasks/id/complete (отметка выполнения)'''
        success = self.storage.complete_task(task_id)
        if success:
            self.send_json(None, 200)   # пустое тело
        else:
            self.send_error_message(404, f'Task with id {task_id} not found')


def run_server(port=8080):
    '''Запускает HTTP-сервер'''
    storage = TaskStorage(TASKS_FILE)
    TaskHTTPHandler.storage = storage

    server_address = ('', port)
    httpd = HTTPServer(server_address, TaskHTTPHandler)

    print(f"Сервер запущен на порту {port}")
    print(f"Файл задач: {storage.filename}")
    print("Доступные эндпоинты:")
    print("  GET  /tasks - получить все задачи")
    print("  POST /tasks - создать новую задачу (body: {\"title\": \"...\", \"priority\": \"low/normal/high\"})")
    print("  POST /tasks/<id>/complete - отметить задачу как выполненную")
    print("\nНажмите Ctrl+C для остановки сервера")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
        httpd.server_close()


if __name__ == '__main__':
    run_server()