#!/usr/bin/env python3
# test_task_manager.py - Тесты для менеджера задач

import unittest
import os
import tempfile
import json
from task_manager import Task, TaskManager

class TestTask(unittest.TestCase):
    """Тесты для класса Task"""
    
    def test_task_creation(self):
        """Тест создания задачи"""
        task = Task(1, "Тестовая задача", "Описание")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Тестовая задача")
        self.assertEqual(task.description, "Описание")
        self.assertFalse(task.completed)
    
    def test_task_to_dict(self):
        """Тест преобразования в словарь"""
        task = Task(1, "Тест", "Описание")
        data = task.to_dict()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['title'], "Тест")
        self.assertEqual(data['description'], "Описание")
        self.assertFalse(data['completed'])
    
    def test_task_from_dict(self):
        """Тест создания из словаря"""
        data = {
            'id': 1,
            'title': 'Тест',
            'description': 'Описание',
            'completed': True,
            'created_at': '2024-01-01T12:00:00'
        }
        task = Task.from_dict(data)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Тест")
        self.assertEqual(task.description, "Описание")
        self.assertTrue(task.completed)
    
    def test_task_str(self):
        """Тест строкового представления"""
        task1 = Task(1, "Задача")
        self.assertTrue(str(task1).startswith("⭕"))
        
        task2 = Task(2, "Готовая задача", completed=True)
        self.assertTrue(str(task2).startswith("✅"))


class TestTaskManager(unittest.TestCase):
    """Тесты для класса TaskManager"""
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = TaskManager(self.temp_file.name)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_add_task(self):
        """Тест добавления задачи"""
        task = self.manager.add_task("Новая задача", "Описание")
        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Новая задача")
        self.assertEqual(task.description, "Описание")
        self.assertEqual(len(self.manager.tasks), 1)
    
    def test_add_multiple_tasks(self):
        """Тест добавления нескольких задач"""
        self.manager.add_task("Задача 1")
        self.manager.add_task("Задача 2")
        self.manager.add_task("Задача 3")
        
        self.assertEqual(len(self.manager.tasks), 3)
        self.assertEqual(self.manager.next_id, 4)
    
    def test_get_task_by_id(self):
        """Тест поиска задачи по ID"""
        self.manager.add_task("Задача 1")
        self.manager.add_task("Задача 2")
        
        task = self.manager.get_task_by_id(2)
        self.assertIsNotNone(task)
        self.assertEqual(task.title, "Задача 2")
        
        task = self.manager.get_task_by_id(999)
        self.assertIsNone(task)
    
    def test_complete_task(self):
        """Тест отметки задачи как выполненной"""
        self.manager.add_task("Задача")
        
        result = self.manager.complete_task(1)
        self.assertTrue(result)
        self.assertTrue(self.manager.tasks[0].completed)
        
        result = self.manager.complete_task(999)
        self.assertFalse(result)
    
    def test_delete_task(self):
        """Тест удаления задачи"""
        self.manager.add_task("Задача 1")
        self.manager.add_task("Задача 2")
        
        result = self.manager.delete_task(1)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(self.manager.tasks[0].title, "Задача 2")
        
        result = self.manager.delete_task(999)
        self.assertFalse(result)
    
    def test_save_and_load(self):
        """Тест сохранения и загрузки задач"""
        self.manager.add_task("Задача 1", "Описание 1")
        self.manager.add_task("Задача 2")
        self.manager.complete_task(1)
        
        # Создаем новый менеджер с тем же файлом
        new_manager = TaskManager(self.temp_file.name)
        
        self.assertEqual(len(new_manager.tasks), 2)
        self.assertEqual(new_manager.tasks[0].title, "Задача 1")
        self.assertTrue(new_manager.tasks[0].completed)
        self.assertEqual(new_manager.tasks[1].title, "Задача 2")
    
    def test_get_stats(self):
        """Тест статистики"""
        self.manager.add_task("Задача 1")
        self.manager.add_task("Задача 2")
        self.manager.add_task("Задача 3")
        self.manager.complete_task(1)
        
        stats = self.manager.get_stats()
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['pending'], 2)


if __name__ == '__main__':
    unittest.main()
