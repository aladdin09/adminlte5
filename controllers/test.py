# -*- coding: utf-8 -*-
"""
Минимальный тестовый контроллер для проверки базовой работы web2py
"""

def index():
    return "Тестовый контроллер работает!"

def test_connection():
    """Детальная диагностика подключения к БД"""
    try:
        result = "Диагностика подключения к БД:\n\n"
        
        # 1. Проверка настроек
        try:
            uri = db._uri
            result += f"URI подключения: {uri.split('@')[0]}@***\n"
        except:
            result += "⚠ Не удалось получить URI\n"
        
        # 2. Проверка драйвера
        try:
            driver = db._adapter.driver
            result += f"Драйвер: {driver}\n"
        except:
            result += "⚠ Не удалось определить драйвер\n"
        
        # 3. Проверка миграции
        try:
            migrate = db._adapter.migrate_enabled
            result += f"Миграция включена: {migrate}\n"
        except:
            result += "⚠ Не удалось проверить миграцию\n"
        
        # 4. Тест подключения
        result += "\nТест подключения:\n"
        try:
            version = db.executesql("SELECT version();")
            result += f"✓ Подключение работает\n"
            result += f"PostgreSQL: {version[0][0][:80]}...\n"
        except Exception as e:
            result += f"✗ Ошибка подключения: {str(e)}\n"
            return result
        
        # 5. Проверка текущего пользователя
        result += "\nТекущий пользователь:\n"
        try:
            user_info = db.executesql("SELECT current_user, current_database();")
            result += f"✓ Пользователь: {user_info[0][0]}\n"
            result += f"✓ База данных: {user_info[0][1]}\n"
        except Exception as e:
            result += f"✗ Ошибка: {str(e)}\n"
        
        # 6. Проверка прав на создание таблиц
        result += "\nПроверка прав:\n"
        try:
            # Пробуем создать тестовую таблицу
            db.executesql("CREATE TABLE IF NOT EXISTS _web2py_test_table (id SERIAL PRIMARY KEY);")
            db.executesql("DROP TABLE IF EXISTS _web2py_test_table;")
            db.commit()
            result += "✓ Права на создание таблиц: есть\n"
        except Exception as e:
            result += f"✗ Права на создание таблиц: {str(e)}\n"
            try:
                db.rollback()
            except:
                pass
        
        # 7. Проверка схемы
        result += "\nПроверка схемы:\n"
        try:
            schemas = db.executesql("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'public';")
            if schemas:
                result += "✓ Схема public существует\n"
            else:
                result += "⚠ Схема public не найдена\n"
        except Exception as e:
            result += f"✗ Ошибка проверки схемы: {str(e)}\n"
        
        # 8. Список существующих таблиц
        result += "\nСуществующие таблицы в БД:\n"
        try:
            tables = db.executesql("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            if tables:
                result += f"Найдено таблиц: {len(tables)}\n"
                for table in tables[:10]:
                    result += f"  - {table[0]}\n"
                if len(tables) > 10:
                    result += f"  ... и еще {len(tables) - 10} таблиц\n"
            else:
                result += "⚠ Таблиц не найдено\n"
        except Exception as e:
            result += f"✗ Ошибка: {str(e)}\n"
        
        return result
    except Exception as e:
        import traceback
        return f"Ошибка диагностики: {str(e)}\n\n{traceback.format_exc()}"

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
        # Откатываем любые незавершенные транзакции
        try:
            db.rollback()
        except:
            pass
        
        tables = db.tables
        result = f"Таблицы в БД ({len(tables)}):\n\n"
        errors = []
        success = []
        
        for table in sorted(tables):
            try:
                # Откатываем транзакцию перед каждым запросом, чтобы избежать проблем
                try:
                    db.rollback()
                except:
                    pass
                
                # Пробуем простой запрос
                count = db(db[table].id > 0).count()
                result += f"  ✓ {table}: {count} записей\n"
                success.append(table)
            except Exception as e:
                error_str = str(e)
                # Откатываем транзакцию после ошибки
                try:
                    db.rollback()
                except:
                    pass
                
                # Проверяем, существует ли таблица
                if "does not exist" in error_str or "relation" in error_str.lower():
                    result += f"  ✗ {table}: таблица не существует\n"
                else:
                    result += f"  ✗ {table}: {error_str[:100]}\n"
                errors.append(f"{table}: {error_str[:200]}")
        
        result += f"\n\nИтого: ✓ работает {len(success)}, ✗ ошибок {len(errors)}"
        
        if errors:
            result += f"\n\nОшибки (первые 10):\n"
            for err in errors[:10]:
                result += f"  - {err}\n"
            if len(errors) > 10:
                result += f"  ... и еще {len(errors) - 10} ошибок\n"
            
            result += f"\n\n💡 Решение: Откройте https://eleotapp.ru/adminlte5/test/create_tables для создания таблиц"
        
        return result
    except Exception as e:
        import traceback
        # Откатываем транзакцию при критической ошибке
        try:
            db.rollback()
        except:
            pass
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

def create_tables_direct():
    """Прямое создание таблиц через обращение к ним (web2py создаст автоматически)"""
    try:
        result = "Прямое создание таблиц (web2py автоматически):\n\n"
        
        db.rollback()
        
        # Проверяем миграцию
        try:
            migrate = getattr(db._adapter, 'migrate_enabled', True)
            result += f"Миграция: {migrate}\n\n"
        except:
            result += "Миграция: не удалось проверить (предполагаем True)\n\n"
        
        all_tables = sorted(db.tables)
        result += f"Таблиц для создания: {len(all_tables)}\n\n"
        
        created = []
        exists = []
        errors = []
        
        for table_name in all_tables:
            try:
                db.rollback()
                
                # Просто обращаемся к таблице - web2py должен создать её автоматически
                # Пробуем выполнить простой SELECT - это заставит создать таблицу
                try:
                    # Пробуем count - это должно создать таблицу если migrate=True
                    count = db(db[table_name].id > 0).count()
                    exists.append(table_name)
                    result += f"✓ {table_name}: существует ({count} записей)\n"
                    db.commit()
                except Exception as count_err:
                    error_str = str(count_err)
                    if "does not exist" in error_str or "relation" in error_str.lower():
                        # Таблица не существует, пробуем создать через insert (пустой)
                        # Это заставит web2py создать таблицу
                        try:
                            # Пробуем вставить пустую запись и сразу удалить
                            # Но лучше просто вызвать _create_table явно
                            db[table_name]._create_table()
                            db.commit()
                            created.append(table_name)
                            result += f"✓ {table_name}: создана\n"
                        except Exception as create_err:
                            # Если _create_table не работает, пробуем через определение заново
                            result += f"✗ {table_name}: ошибка создания - {str(create_err)[:150]}\n"
                            errors.append(f"{table_name}: {str(create_err)[:200]}")
                            db.rollback()
                    else:
                        result += f"✗ {table_name}: ошибка - {error_str[:150]}\n"
                        errors.append(f"{table_name}: {error_str[:200]}")
                        db.rollback()
                        
            except Exception as e:
                db.rollback()
                result += f"✗ {table_name}: критическая ошибка - {str(e)[:150]}\n"
                errors.append(f"{table_name}: {str(e)[:200]}")
        
        result += f"\n\nИтого: создано {len(created)}, существует {len(exists)}, ошибок {len(errors)}"
        
        if errors:
            result += f"\n\nОшибки:\n"
            for err in errors[:15]:
                result += f"  - {err}\n"
        
        if created or exists:
            result += f"\n\n✅ Обработано {len(created) + len(exists)} таблиц!"
            result += f"\nПроверьте: https://eleotapp.ru/adminlte5/test/test_tables"
        
        return result
    except Exception as e:
        import traceback
        try:
            db.rollback()
        except:
            pass
        return f"Ошибка: {str(e)}\n\n{traceback.format_exc()}"

def create_tables_force():
    """Принудительное создание таблиц через прямое выполнение SQL"""
    try:
        result = "Принудительное создание таблиц:\n\n"
        
        # Откатываем транзакции
        try:
            db.rollback()
        except:
            pass
        
        # Проверяем подключение
        try:
            test_query = db.executesql("SELECT version();")
            result += f"✓ Подключение к БД работает\n"
            result += f"PostgreSQL версия: {test_query[0][0][:50]}...\n\n"
        except Exception as e:
            result += f"✗ Ошибка подключения: {str(e)}\n\n"
            return result
        
        all_tables = sorted(db.tables)
        result += f"Таблиц для создания: {len(all_tables)}\n\n"
        
        created = []
        errors = []
        
        for table_name in all_tables:
            try:
                db.rollback()
                
                table = db[table_name]
                
                # Получаем SQL для создания таблицы
                try:
                    # Пробуем получить SQL через адаптер
                    sql = table._create_sql()
                    if sql:
                        # Выполняем SQL напрямую
                        db.executesql(sql)
                        db.commit()
                        created.append(table_name)
                        result += f"✓ {table_name}: создана через SQL\n"
                    else:
                        # Если SQL не получен, пробуем обычный способ
                        table._create_table()
                        db.commit()
                        created.append(table_name)
                        result += f"✓ {table_name}: создана\n"
                except Exception as sql_err:
                    error_str = str(sql_err)
                    db.rollback()
                    
                    if "already exists" in error_str.lower():
                        created.append(table_name)
                        result += f"✓ {table_name}: уже существует\n"
                    else:
                        result += f"✗ {table_name}: {error_str[:200]}\n"
                        errors.append(f"{table_name}: {error_str[:200]}")
                        
            except Exception as e:
                db.rollback()
                result += f"✗ {table_name}: {str(e)[:200]}\n"
                errors.append(f"{table_name}: {str(e)[:200]}")
        
        result += f"\n\nИтого: создано {len(created)}, ошибок {len(errors)}"
        
        if errors:
            result += f"\n\nОшибки:\n"
            for err in errors[:10]:
                result += f"  - {err}\n"
        
        return result
    except Exception as e:
        import traceback
        try:
            db.rollback()
        except:
            pass
        return f"Ошибка: {str(e)}\n\n{traceback.format_exc()}"

def create_tables_simple():
    """Простое создание таблиц - вызывает _create_table для каждой"""
    try:
        result = "Простое создание таблиц:\n\n"
        
        # Откатываем любые незавершенные транзакции
        try:
            db.rollback()
        except:
            pass
        
        # Проверяем миграцию
        try:
            migrate_enabled = db._adapter.migrate_enabled
            result += f"Миграция включена: {migrate_enabled}\n"
            if not migrate_enabled:
                return "❌ Миграция отключена! Включите migrate=true в appconfig.ini"
        except Exception as e:
            result += f"⚠ Не удалось проверить миграцию: {str(e)}\n"
        
        # Проверяем подключение к БД
        try:
            db_version = db._adapter.driver
            result += f"Драйвер БД: {db_version}\n"
        except:
            pass
        
        all_tables = sorted(db.tables)
        result += f"\nТаблиц для создания: {len(all_tables)}\n\n"
        
        created = []
        exists = []
        errors = []
        
        for table_name in all_tables:
            try:
                # Откатываем перед каждой таблицей
                try:
                    db.rollback()
                except:
                    pass
                
                # Пробуем создать таблицу
                table = db[table_name]
                
                # Пробуем _create_table
                try:
                    table._create_table()
                    # Коммитим создание
                    try:
                        db.commit()
                        created.append(table_name)
                        result += f"✓ {table_name}: создана\n"
                    except Exception as commit_err:
                        result += f"⚠ {table_name}: создана, но ошибка коммита - {str(commit_err)}\n"
                        try:
                            db.rollback()
                        except:
                            pass
                        # Пробуем еще раз закоммитить
                        try:
                            db.commit()
                            created.append(table_name)
                            result += f"  ✓ Коммит успешен при повторной попытке\n"
                        except:
                            errors.append(f"{table_name}: ошибка коммита - {str(commit_err)}")
                            
                except Exception as create_err:
                    error_str = str(create_err)
                    # Откатываем после ошибки
                    try:
                        db.rollback()
                    except:
                        pass
                    
                    # Проверяем, может таблица уже существует
                    if "already exists" in error_str.lower() or "duplicate" in error_str.lower() or "уже существует" in error_str.lower():
                        exists.append(table_name)
                        result += f"✓ {table_name}: уже существует\n"
                    else:
                        # Показываем детальную ошибку
                        result += f"✗ {table_name}: {error_str}\n"
                        errors.append(f"{table_name}: {error_str}")
                        
            except Exception as e:
                error_msg = str(e)
                result += f"✗ {table_name}: критическая ошибка - {error_msg}\n"
                errors.append(f"{table_name}: {error_msg}")
                # Откатываем после ошибки
                try:
                    db.rollback()
                except:
                    pass
        
        result += f"\n\nИтого: создано {len(created)}, существует {len(exists)}, ошибок {len(errors)}"
        
        if errors:
            result += f"\n\n❌ Ошибки ({len(errors)}):\n"
            for err in errors[:15]:
                result += f"  - {err}\n"
            if len(errors) > 15:
                result += f"  ... и еще {len(errors) - 15} ошибок\n"
        
        if created or exists:
            result += f"\n\n✅ Обработано {len(created) + len(exists)} таблиц!"
            result += f"\nПроверьте: https://eleotapp.ru/adminlte5/test/test_tables"
        
        return result
    except Exception as e:
        import traceback
        try:
            db.rollback()
        except:
            pass
        return f"Критическая ошибка: {str(e)}\n\n{traceback.format_exc()}"

def create_tables():
    """Принудительное создание таблиц через обращение к ним"""
    try:
        # Откатываем любые незавершенные транзакции перед началом
        try:
            db.rollback()
        except:
            pass
        
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
                # Откатываем транзакцию перед каждой таблицей
                try:
                    db.rollback()
                except:
                    pass
                
                # Пробуем выполнить простой запрос - это заставит web2py создать таблицу
                # если она не существует
                try:
                    # Простой SELECT с LIMIT 0 - не вернет данных, но создаст таблицу если нужно
                    db(db[table_name].id > 0).select(limitby=(0, 1))
                    exists.append(table_name)
                    result += f"✓ {table_name}: существует\n"
                    # Коммитим успешную проверку
                    try:
                        db.commit()
                    except:
                        pass
                except Exception as query_err:
                    error_str = str(query_err)
                    # Откатываем транзакцию после ошибки
                    try:
                        db.rollback()
                    except:
                        pass
                    
                    if "does not exist" in error_str or "relation" in error_str.lower():
                        # Таблица не существует, пытаемся создать через _create_table
                        try:
                            db[table_name]._create_table()
                            # Коммитим создание таблицы
                            try:
                                db.commit()
                            except Exception as commit_err:
                                result += f"  ⚠ Ошибка коммита: {str(commit_err)}\n"
                                try:
                                    db.rollback()
                                except:
                                    pass
                            
                            created.append(table_name)
                            result += f"✓ {table_name}: создана\n"
                        except Exception as create_err:
                            result += f"✗ {table_name}: ошибка создания - {str(create_err)[:200]}\n"
                            errors.append(f"{table_name}: {str(create_err)[:200]}")
                            # Откатываем после ошибки создания
                            try:
                                db.rollback()
                            except:
                                pass
                    else:
                        # Другая ошибка
                        result += f"✗ {table_name}: ошибка запроса - {error_str[:200]}\n"
                        errors.append(f"{table_name}: {error_str[:200]}")
                        # Откатываем после ошибки
                        try:
                            db.rollback()
                        except:
                            pass
                        
            except Exception as e:
                error_msg = str(e)
                result += f"✗ {table_name}: ошибка - {error_msg[:200]}\n"
                errors.append(f"{table_name}: {error_msg[:200]}")
                # Откатываем после ошибки
                try:
                    db.rollback()
                except:
                    pass
        
        # Финальный коммит
        try:
            db.commit()
            result += "\n✓ Финальная транзакция закоммичена"
        except Exception as commit_err:
            result += f"\n⚠ Ошибка финального коммита: {str(commit_err)}"
            try:
                db.rollback()
                result += " (откат выполнен)"
            except:
                pass
        
        result += f"\n\nИтого: создано {len(created)}, существует {len(exists)}, ошибок {len(errors)}"
        if errors:
            result += f"\n\nОшибки (первые 10):\n"
            for err in errors[:10]:
                result += f"  - {err}\n"
            if len(errors) > 10:
                result += f"  ... и еще {len(errors) - 10} ошибок\n"
        
        if created:
            result += f"\n\n✅ Успешно создано {len(created)} таблиц!\n"
            result += "Попробуйте открыть: https://eleotapp.ru/adminlte5/default/index"
        elif not errors and exists:
            result += f"\n\n✅ Все таблицы уже существуют!\n"
            result += "Попробуйте открыть: https://eleotapp.ru/adminlte5/default/index"
        
        return result
    except Exception as e:
        import traceback
        # Откатываем при критической ошибке
        try:
            db.rollback()
        except:
            pass
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
