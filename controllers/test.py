# -*- coding: utf-8 -*-
"""
Минимальный тестовый контроллер для проверки базовой работы web2py
"""

def index():
    return "Тестовый контроллер работает!"

def test_db():
    try:
        count = db(db.customers.id > 0).count()
        return f"База данных работает. Клиентов: {count}"
    except Exception as e:
        return f"Ошибка базы данных: {str(e)}"

def test_import():
    try:
        from dashboard_data import get_dashboard_data, get_status_color
        return "Импорт dashboard_data успешен"
    except Exception as e:
        return f"Ошибка импорта dashboard_data: {str(e)}"
