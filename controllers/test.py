# -*- coding: utf-8 -*-
"""
Минимальный тестовый контроллер для проверки базовой работы web2py
"""

def index():
    return "Тестовый контроллер работает!"

def test_db():
    try:
        # Пробуем разные варианты запросов
        result = "Тест подключения к БД:\n\n"
        
        # Вариант 1: Простой SELECT
        try:
            rows = db().select(db.customers.ALL, limitby=(0, 1))
            result += f"✓ SELECT работает: {len(rows)} строк\n"
        except Exception as e:
            result += f"✗ SELECT ошибка: {str(e)}\n"
            import traceback
            result += f"Traceback:\n{traceback.format_exc()}\n"
        
        # Вариант 2: COUNT без условия
        try:
            count = db().select(db.customers.id, limitby=(0, 1000))
            result += f"✓ SELECT с limit работает: {len(count)} строк\n"
        except Exception as e:
            result += f"✗ SELECT с limit ошибка: {str(e)}\n"
        
        # Вариант 3: COUNT с условием id > 0
        try:
            count = db(db.customers.id > 0).count()
            result += f"✓ COUNT с условием работает: {count} записей\n"
        except Exception as e:
            result += f"✗ COUNT с условием ошибка: {str(e)}\n"
            import traceback
            result += f"Traceback:\n{traceback.format_exc()}\n"
        
        # Вариант 4: COUNT без условия (альтернативный синтаксис)
        try:
            count = db(db.customers).count()
            result += f"✓ COUNT без условия работает: {count} записей\n"
        except Exception as e:
            result += f"✗ COUNT без условия ошибка: {str(e)}\n"
        
        return result
    except Exception as e:
        import traceback
        return f"Критическая ошибка базы данных: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

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
        result = f"Таблицы в БД ({len(tables)}):\n\n"
        errors = []
        for table in sorted(tables):
            try:
                count = db(db[table].id > 0).count()
                result += f"  ✓ {table}: {count} записей\n"
            except Exception as e:
                error_msg = f"  ✗ {table}: {str(e)}"
                result += error_msg + "\n"
                errors.append(f"{table}: {str(e)}")
        if errors:
            result += f"\n\nОшибки ({len(errors)}):\n"
            for err in errors[:5]:  # Показываем первые 5 ошибок
                result += f"  - {err}\n"
            if len(errors) > 5:
                result += f"  ... и еще {len(errors) - 5} ошибок\n"
        return result
    except Exception as e:
        import traceback
        return f"Ошибка проверки таблиц: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

def test_table_structure():
    """Проверка структуры конкретной таблицы"""
    table_name = request.vars.get('table', 'customers')
    try:
        if table_name not in db.tables:
            return f"Таблица '{table_name}' не найдена. Доступные таблицы: {', '.join(sorted(db.tables))}"
        
        # Получаем структуру таблицы
        table = db[table_name]
        result = f"Структура таблицы '{table_name}':\n\n"
        result += f"Поля ({len(table.fields)}):\n"
        for field in table.fields:
            field_obj = table[field]
            result += f"  - {field}: {field_obj.type}\n"
        
        # Пробуем простой запрос
        result += f"\nПопытка запроса:\n"
        try:
            # Просто SELECT без условий
            rows = db(table_name).select(limitby=(0, 1))
            result += f"  ✓ SELECT работает, получено строк: {len(rows)}\n"
        except Exception as e:
            result += f"  ✗ SELECT ошибка: {str(e)}\n"
        
        # Пробуем COUNT
        result += f"\nПопытка COUNT:\n"
        try:
            count = db(table_name).count()
            result += f"  ✓ COUNT работает: {count} записей\n"
        except Exception as e:
            result += f"  ✗ COUNT ошибка: {str(e)}\n"
            import traceback
            result += f"\nTraceback:\n{traceback.format_exc()}\n"
        
        return result
    except Exception as e:
        import traceback
        return f"Ошибка проверки структуры таблицы: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

def create_tables():
    """Принудительное создание таблиц через обращение к ним"""
    try:
        result = "Создание таблиц в базе данных:\n\n"
        
        # Проверяем настройки миграции
        try:
            migrate_enabled = db._adapter.migrate_enabled
            result += f"Миграция включена: {migrate_enabled}\n\n"
        except:
            result += "⚠ Не удалось проверить настройки миграции\n\n"
            migrate_enabled = True
        
        if not migrate_enabled:
            result += "⚠ ВНИМАНИЕ: Миграция отключена! Включите migrate=true в appconfig.ini\n\n"
            return result + "\nНельзя создать таблицы при отключенной миграции!"
        
        # Получаем список всех определенных таблиц
        all_tables = list(db.tables)
        result += f"Таблиц определено в моделях: {len(all_tables)}\n\n"
        
        created = []
        exists = []
        errors = []
        
        # Пробуем создать/проверить каждую таблицу
        # Web2py создаст таблицу автоматически при первом обращении, если migrate=True
        for table_name in sorted(all_tables):
            try:
                # Пробуем выполнить простой запрос - это заставит web2py создать таблицу
                # если она не существует
                try:
                    # Простой SELECT с LIMIT 0 - не вернет данных, но создаст таблицу если нужно
                    db(db[table_name].id > 0).select(limitby=(0, 1))
                    exists.append(table_name)
                    result += f"✓ {table_name}: существует\n"
                except Exception as query_err:
                    error_str = str(query_err)
                    if "does not exist" in error_str or "relation" in error_str.lower():
                        # Таблица не существует, пытаемся создать через _create_table
                        try:
                            db[table_name]._create_table()
                            created.append(table_name)
                            result += f"✓ {table_name}: создана\n"
                        except Exception as create_err:
                            result += f"✗ {table_name}: ошибка создания - {str(create_err)}\n"
                            errors.append(f"{table_name}: {str(create_err)}")
                    else:
                        # Другая ошибка
                        result += f"✗ {table_name}: ошибка запроса - {error_str}\n"
                        errors.append(f"{table_name}: {error_str}")
                        
            except Exception as e:
                error_msg = str(e)
                result += f"✗ {table_name}: ошибка - {error_msg}\n"
                errors.append(f"{table_name}: {error_msg}")
        
        # Коммитим транзакцию
        try:
            db.commit()
            result += "\n✓ Транзакция закоммичена"
        except Exception as commit_err:
            result += f"\n⚠ Ошибка коммита: {str(commit_err)}"
            try:
                db.rollback()
                result += " (откат выполнен)"
            except:
                pass
        
        result += f"\n\nИтого: создано {len(created)}, существует {len(exists)}, ошибок {len(errors)}"
        if errors:
            result += f"\n\nОшибки:\n"
            for err in errors[:10]:
                result += f"  - {err}\n"
        
        if created:
            result += f"\n\n✓ Успешно создано {len(created)} таблиц! Попробуйте открыть:\n"
            result += "https://eleotapp.ru/adminlte5/default/index"
        
        return result
    except Exception as e:
        import traceback
        return f"Ошибка создания таблиц: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

def test_simple_query():
    """Простой тест запроса к customers"""
    try:
        # Самый простой запрос
        result = "Тест простых запросов:\n\n"
        
        # 1. Проверка существования таблицы
        if 'customers' not in db.tables:
            return "Таблица 'customers' не найдена!"
        result += "✓ Таблица 'customers' существует\n"
        
        # 2. Простой SELECT без условий
        try:
            rows = db().select(db.customers.ALL, limitby=(0, 5))
            result += f"✓ SELECT работает: получено {len(rows)} строк\n"
        except Exception as e:
            result += f"✗ SELECT ошибка: {str(e)}\n"
            import traceback
            result += f"Traceback:\n{traceback.format_exc()}\n"
        
        # 3. COUNT без условий
        try:
            count = db().select(db.customers.id, limitby=(0, 1))
            result += f"✓ Простой SELECT с limit работает\n"
        except Exception as e:
            result += f"✗ SELECT с limit ошибка: {str(e)}\n"
        
        # 4. COUNT с условием
        try:
            # Пробуем разные варианты
            count1 = db(db.customers.id > 0).count()
            result += f"✓ COUNT с условием работает: {count1} записей\n"
        except Exception as e:
            result += f"✗ COUNT с условием ошибка: {str(e)}\n"
            import traceback
            result += f"Traceback:\n{traceback.format_exc()}\n"
        
        return result
    except Exception as e:
        import traceback
        return f"Ошибка: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
