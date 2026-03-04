import json


class TaskStorage:
    """Класс для хранения и управления задачами"""
    def __init__(self, filename):
        self.__filename = filename
        self.__tasks = []
        self._load()

    def next_id(self):
        if not self.__tasks:
            return 1
        return max(task["id"] for task in self.__tasks) + 1

    def _load(self):
        """Загружает задачи из файла"""
        try:
            with open(self.__filename, "r", encoding="utf-8") as f:
                self.__tasks = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.__tasks = []

    def save(self):
        """Сохраняет задачи в файл"""
        with open(self.__filename, 'w', encoding='utf-8') as f:
            json.dump(self.__tasks, f, ensure_ascii=False, indent=2)

    def get_all(self):
        """Возвращает список всех задач"""
        return self.__tasks

    def find_task_id(self, task_id):
        """Ищет задачу по id"""
        for task in self.__tasks:
            if task['id'] == task_id:
                return task
        return None

    def add_task(self, task):
        """Добавляет новую задачу"""
        self.__tasks.append(task)
        self.save()

    def complete_task(self, task_id):
        """Отмечает задачу выполненной"""
        task = self.find_task_id(task_id)
        if task:
            task['isDone'] = True
            self.save()
            return True
        return False