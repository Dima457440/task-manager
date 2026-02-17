import json
import os
from datetime import datetime

class Task:
    """Класс задачи"""
    def __init__(self, id, title, description="", completed=False, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание задачи из словаря"""
        return cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            completed=data.get('completed', False),
            created_at=data.get('created_at')
        )
    
    def __str__(self):
        status = "✅" if self.completed else "⭕"
        return f"{status} [{self.id}] {self.title}"


class TaskManager:
    """Менеджер задач"""
    def __init__(self, filename='tasks.json'):
        self.filename = filename
        self.tasks = []
        self.load_tasks()
        self.next_id = self._get_next_id()

    def _get_next_id(self):
        """Получение следующего ID"""
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def load_tasks(self):
        """Загрузка задач из файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
            except (json.JSONDecodeError, FileNotFoundError):
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """Сохранение задач в файл"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([task.to_dict() for task in self.tasks], f, ensure_ascii=False, indent=2)

    def add_task(self, title, description=""):
        """Добавление новой задачи"""
        task = Task(self.next_id, title, description)
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return task

    def get_all_tasks(self):
        """Получение всех задач"""
        return self.tasks

    def get_task_by_id(self, task_id):
        """Получение задачи по ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def complete_task(self, task_id):
        """Отметка задачи как выполненной"""
        task = self.get_task_by_id(task_id)
        if task:
            task.completed = True
            self.save_tasks()
            return True
        return False

    def delete_task(self, task_id):
        """Удаление задачи"""
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            return True
        return False

    def edit_task(self, task_id, title=None, description=None):
        """Редактирование задачи"""
        task = self.get_task_by_id(task_id)
        if task:
            if title:
                task.title = title
            if description is not None:
                task.description = description
            self.save_tasks()
            return True
        return False

    def get_stats(self):
        """Получение статистики"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.completed)
        pending = total - completed
        return {
            'total': total,
            'completed': completed,
            'pending': pending
        }


def print_menu():
    """Вывод меню"""
    print("\n" + "="*50)
    print("МЕНЕДЖЕР ЗАДАЧ".center(50))
    print("="*50)
    print("1. 📋 Показать все задачи")
    print("2. ➕ Добавить задачу")
    print("3. ✏️ Редактировать задачу")
    print("4. ✅ Отметить задачу как выполненную")
    print("5. ❌ Удалить задачу")
    print("6. 📊 Статистика")
    print("7. 🚪 Выход")
    print("="*50)


def show_tasks(tasks):
    """Показать задачи"""
    if not tasks:
        print("\n📭 Задач пока нет.")
        return
    
    print("\n" + "-"*50)
    print("СПИСОК ЗАДАЧ".center(50))
    print("-"*50)
    
    for task in tasks:
        print(task)
        if task.description:
            print(f"   📝 {task.description}")


def main():
    """Основная функция"""
    manager = TaskManager()
    
    while True:
        print_menu()
        choice = input("\nВыберите действие (1-7): ").strip()
        
        if choice == '1':
            show_tasks(manager.get_all_tasks())
        
        elif choice == '2':
            print("\n➡️  Добавление новой задачи")
            title = input("Введите название задачи: ").strip()
            if not title:
                print("❌ Название не может быть пустым!")
                continue
            description = input("Введите описание (необязательно): ").strip()
            task = manager.add_task(title, description)
            print(f"✅ Задача '{task.title}' успешно добавлена с ID {task.id}")
        
        elif choice == '3':
            tasks = manager.get_all_tasks()
            if not tasks:
                print("\n📭 Нет задач для редактирования.")
                continue
            
            show_tasks(tasks)
            try:
                task_id = int(input("\nВведите ID задачи для редактирования: "))
                task = manager.get_task_by_id(task_id)
                if task:
                    print(f"\nРедактирование задачи: {task.title}")
                    new_title = input("Новое название (Enter - оставить без изменений): ").strip()
                    new_desc = input("Новое описание (Enter - оставить без изменений): ").strip()
                    
                    if manager.edit_task(
                        task_id, 
                        title=new_title if new_title else None,
                        description=new_desc if new_desc else None
                    ):
                        print(f"✅ Задача с ID {task_id} обновлена!")
                    else:
                        print(f"❌ Ошибка при обновлении задачи!")
                else:
                    print(f"❌ Задача с ID {task_id} не найдена!")
            except ValueError:
                print("❌ Введите корректный ID!")
        
        elif choice == '4':
            tasks = manager.get_all_tasks()
            if not tasks:
                print("\n📭 Нет задач для отметки.")
                continue
            
            show_tasks([t for t in tasks if not t.completed])
            try:
                task_id = int(input("\nВведите ID задачи для отметки: "))
                if manager.complete_task(task_id):
                    print(f"✅ Задача с ID {task_id} отмечена как выполненная!")
                else:
                    print(f"❌ Задача с ID {task_id} не найдена!")
            except ValueError:
                print("❌ Введите корректный ID!")
        
        elif choice == '5':
            tasks = manager.get_all_tasks()
            if not tasks:
                print("\n📭 Нет задач для удаления.")
                continue
            
            show_tasks(tasks)
            try:
                task_id = int(input("\nВведите ID задачи для удаления: "))
                task = manager.get_task_by_id(task_id)
                if task:
                    confirm = input(f"Удалить задачу '{task.title}'? (д/н): ").strip().lower()
                    if confirm in ['д', 'да', 'y', 'yes']:
                        if manager.delete_task(task_id):
                            print(f"✅ Задача с ID {task_id} удалена!")
                    else:
                        print("❌ Удаление отменено.")
                else:
                    print(f"❌ Задача с ID {task_id} не найдена!")
            except ValueError:
                print("❌ Введите корректный ID!")
        
        elif choice == '6':
            stats = manager.get_stats()
            print("\n" + "-"*50)
            print("СТАТИСТИКА".center(50))
            print("-"*50)
            print(f"📊 Всего задач: {stats['total']}")
            print(f"✅ Выполнено: {stats['completed']}")
            print(f"⭕ В ожидании: {stats['pending']}")
            
            if stats['total'] > 0:
                progress = stats['completed'] / stats['total'] * 100
                print(f"📈 Прогресс: {progress:.1f}%")
                
                bar_length = 20
                filled = int(bar_length * stats['completed'] / stats['total'])
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"   [{bar}]")
        
        elif choice == '7':
            print("\n👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор. Пожалуйста, выберите 1-7.")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем.")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")