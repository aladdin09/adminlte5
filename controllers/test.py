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
        import traceback
        return f"Ошибка импорта dashboard_data: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

def test_dashboard_data():
    """Тест вызова get_dashboard_data"""
    try:
        from dashboard_data import get_dashboard_data
        data = get_dashboard_data(db, request)
        return f"get_dashboard_data работает! Ключи: {list(data.keys())}"
    except Exception as e:
        import traceback
        return f"Ошибка в get_dashboard_data: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

def test_tables():
    """Проверка существования таблиц"""
    try:
        tables = db.tables
        result = f"Таблицы в БД ({len(tables)}):\n"
        for table in sorted(tables):
            try:
                count = db(db[table].id > 0).count()
                result += f"  - {table}: {count} записей\n"
            except:
                result += f"  - {table}: ошибка подсчета\n"
        return result
    except Exception as e:
        import traceback
        return f"Ошибка проверки таблиц: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
