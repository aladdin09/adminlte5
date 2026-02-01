# Создание таблиц - Финальное решение

## ✅ Диагностика показала:
- ✓ Подключение работает
- ✓ Пользователь: smetadoma02
- ✓ База данных: smetadoma02_db
- ✓ Права на создание таблиц: есть
- ✓ Схема public существует
- ⚠ Таблиц не найдено (нужно создать)

## 🚀 Способы создания таблиц:

### Способ 1: Через функцию create_tables_simple (РЕКОМЕНДУЕТСЯ)

Откройте в браузере:
```
https://eleotapp.ru/adminlte5/test/create_tables_simple
```

Эта функция вызывает `_create_table()` для каждой таблицы.

### Способ 2: Через appadmin (САМЫЙ ПРОСТОЙ)

Откройте:
```
https://eleotapp.ru/adminlte5/appadmin
```

Web2py автоматически создаст таблицы при первом обращении к базе данных через интерфейс appadmin.

### Способ 3: Через прямое обращение к таблицам

Откройте:
```
https://eleotapp.ru/adminlte5/test/create_tables_direct
```

Эта функция просто обращается к таблицам, и web2py создаст их автоматически.

### Способ 4: Через web2py shell (если другие не работают)

На боевом сервере через SSH:

```bash
cd /opt/web2py
python3 web2py.py -S adminlte5 -M
```

В консоли web2py выполните:

```python
# Создаем таблицы по одной
db.customers._create_table()
db.commit()

db.projects._create_table()
db.commit()

db.project_statuses._create_table()
db.commit()

db.complect_statuses._create_table()
db.commit()

db.next_steps._create_table()
db.commit()

db.complects._create_table()
db.commit()

db.complect_items._create_table()
db.commit()

db.orders._create_table()
db.commit()

db.order_items._create_table()
db.commit()

db.nomenclature_items._create_table()
db.commit()

# Таблицы auth создаются автоматически при определении auth
# Но можно проверить:
db.auth_user._create_table()
db.commit()

# Выйти
exit()
```

## 🔍 Проверка после создания:

1. **Проверка таблиц:**
   ```
   https://eleotapp.ru/adminlte5/test/test_tables
   ```

2. **Проверка через psql:**
   ```bash
   psql -h localhost -U smetadoma02 -d smetadoma02_db -c "\dt"
   ```

3. **Главная страница:**
   ```
   https://eleotapp.ru/adminlte5/default/index
   ```

## ⚠️ Если таблицы все еще не создаются:

1. **Проверьте логи web2py:**
   ```bash
   LATEST_ERROR=$(ls -t /opt/web2py/applications/adminlte5/errors/ | head -1)
   tail -200 "/opt/web2py/applications/adminlte5/errors/$LATEST_ERROR"
   ```

2. **Проверьте, что миграция действительно включена:**
   ```bash
   grep -i migrate /opt/web2py/applications/adminlte5/private/appconfig.ini
   ```
   Должно быть: `migrate = true`

3. **Попробуйте создать таблицу вручную через psql:**
   ```bash
   psql -h localhost -U smetadoma02 -d smetadoma02_db -c "CREATE TABLE test_manual (id SERIAL PRIMARY KEY);"
   ```
   Если это работает, значит проблема в web2py, а не в правах.

4. **Очистите кэш web2py:**
   ```bash
   find /opt/web2py/applications/adminlte5 -type d -name __pycache__ -exec rm -r {} +
   ```

5. **Перезапустите web2py** (если используется как сервис):
   ```bash
   sudo systemctl restart web2py
   # или
   sudo service web2py restart
   ```
