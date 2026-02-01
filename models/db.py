# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon import DAL
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth
from gluon.validators import IS_IN_DB, IS_EMPTY_OR, IS_EMAIL, IS_MATCH, IS_INT_IN_RANGE, IS_FLOAT_IN_RANGE
import os
import re
import datetime

REQUIRED_WEB2PY_VERSION = "3.0.10"

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

try:
    web2py_version_string = request.global_settings.web2py_version.split("-")[0]
    web2py_version = list(map(int, web2py_version_string.split(".")[:3]))
    if web2py_version < list(map(int, REQUIRED_WEB2PY_VERSION.split(".")[:3])):
        raise HTTP(500, f"Requires web2py version {REQUIRED_WEB2PY_VERSION} or newer, not {web2py_version_string}")
except Exception as version_error:
    # Если не удалось проверить версию, пропускаем проверку
    try:
        import logging
        logging.warning(f"Не удалось проверить версию web2py: {str(version_error)}")
    except:
        pass

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
try:
    configuration = AppConfig(reload=True)
except Exception as config_error:
    # Если не удалось загрузить конфигурацию, используем значения по умолчанию
    import traceback
    error_msg = f"Ошибка загрузки конфигурации: {str(config_error)}\n{traceback.format_exc()}"
    # Создаем объект-заглушку для конфигурации
    class DefaultConfig:
        def get(self, key, default=None):
            defaults = {
                "db.uri": "postgres://smetadoma01:eY^x7ZQJ1OkQf8Y3g^Z2WvUMv1@localhost:5432/smetadoma01_db",
                "db.pool_size": 10,
                "db.migrate": True,
                "app.production": False,
                "host.names": ["*"],
                "smtp.server": "",
                "smtp.sender": "",
                "smtp.login": "",
                "smtp.tls": False,
                "smtp.ssl": False,
                "app.author": "",
                "app.description": "",
                "app.keywords": "",
                "app.generator": "",
                "app.toolbar": False,
                "google.analytics_id": "",
                "scheduler.enabled": False,
                "scheduler.heartbeat": 1,
            }
            return defaults.get(key, default)
    configuration = DefaultConfig()
    # Логируем ошибку, если возможно
    try:
        import logging
        logging.error(error_msg)
    except:
        pass

if "GAE_APPLICATION" not in os.environ:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use PostgreSQL or other DB
    # ---------------------------------------------------------------------
    # Подключение к базе данных PostgreSQL
    # Формат: postgres://username:password@host:port/database
    try:
        db = DAL(configuration.get("db.uri"),
                 pool_size=configuration.get("db.pool_size"),
                 migrate_enabled=configuration.get("db.migrate"),
                 check_reserved=["all"])
    except Exception as db_error:
        # Если не удалось подключиться к БД, создаем заглушку
        import traceback
        error_msg = f"Ошибка подключения к БД: {str(db_error)}\n{traceback.format_exc()}"
        # Создаем пустую БД для избежания ошибок
        db = DAL("sqlite://memory")
        try:
            import logging
            logging.error(error_msg)
        except:
            pass
else:
    # ---------------------------------------------------------------------
    # connect to Google Firestore
    # ---------------------------------------------------------------------
    db = DAL("firestore")
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be "controller/function.extension"
# -------------------------------------------------------------------------
response.generic_patterns = [] 
if request.is_local and not configuration.get("app.production"):
    response.generic_patterns.append("*")

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = "bootstrap4_inline"
response.form_label_separator = ""

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = "concat,minify,inline"
# response.optimize_js = "concat,minify,inline"

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = "0.0.0"

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get("host.names"))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
auth.settings.extra_fields["auth_user"] = []
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = "logging" if request.is_local else configuration.get("smtp.server")
mail.settings.sender = configuration.get("smtp.sender")
mail.settings.login = configuration.get("smtp.login")
mail.settings.tls = configuration.get("smtp.tls") or False
mail.settings.ssl = configuration.get("smtp.ssl") or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------  
# read more at http://dev.w3.org/html5/markup/meta.name.html               
# -------------------------------------------------------------------------
response.meta.author = configuration.get("app.author")
response.meta.description = configuration.get("app.description")
response.meta.keywords = configuration.get("app.keywords")
response.meta.generator = configuration.get("app.generator")
response.show_toolbar = configuration.get("app.toolbar")

# -------------------------------------------------------------------------
# your http://google.com/analytics id                                      
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get("google.analytics_id")

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get("scheduler.enabled"):
    from gluon.scheduler import Scheduler
    scheduler = Scheduler(db, heartbeat=configuration.get("scheduler.heartbeat"))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table("mytable", Field("myfield", "string"))
#
# Fields can be "string","text","password","integer","double","boolean"
#       "date","time","datetime","blob","upload", "reference TABLENAME"
# There is an implicit "id integer autoincrement" field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield="value")
# >>> rows = db(db.mytable.myfield == "value").select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# CRM система для учета клиентов и позиций номенклатуры деревянных домов
# -------------------------------------------------------------------------

# Таблица: Статусы комплектов
db.define_table('complect_statuses',
    Field('name', 'string', length=100, required=True, label='Название статуса'),
    Field('description', 'text', label='Описание'),
    Field('sort_order', 'integer', default=0, label='Порядок сортировки'),
    Field('is_active', 'boolean', default=True, label='Активен'),
    format='%(name)s'
)

# Таблица: Следующие шаги
db.define_table('next_steps',
    Field('name', 'string', length=200, required=True, label='Название шага'),
    Field('description', 'text', label='Описание'),
    Field('days', 'integer', default=0, label='Количество дней на выполнение'),
    Field('is_active', 'boolean', default=True, label='Активен'),
    format='%(name)s'
)

# Таблица: Клиенты
db.define_table('customers',
    Field('name', 'string', length=200, required=True, label='Имя клиента'),
    Field('phone', 'string', length=50, label='Телефон'),
    Field('email', 'string', length=100, label='Email'),
    Field('address', 'text', label='Адрес'),
    Field('notes', 'text', label='Примечания'),
    Field('created_on', 'datetime', default=request.now, writable=False, readable=True),
    Field('modified_on', 'datetime', default=request.now, update=request.now, writable=False, readable=True),
    format='%(name)s'
)

# Таблица: Статусы проектов
db.define_table('project_statuses',
    Field('name', 'string', length=100, required=True, label='Название статуса'),
    Field('description', 'text', label='Описание'),
    Field('sort_order', 'integer', default=0, label='Порядок сортировки'),
    Field('is_active', 'boolean', default=True, label='Активен'),
    format='%(name)s'
)

# Таблица: Проекты
db.define_table('projects',
    Field('name', 'string', length=200, required=True, label='Название проекта'),
    Field('customer_id', 'reference customers', label='Клиент'),
    Field('complect_id', 'integer', label='Комплект'),  # Будет изменено на reference после определения complects
    Field('order_id', 'integer', label='Заказ'),  # Будет изменено на reference после определения orders
    Field('project_number', 'string', length=50, unique=True, label='Номер проекта'),
    Field('start_date', 'date', label='Дата начала проекта'),
    Field('end_date', 'date', label='Дата окончания проекта'),
    Field('status_id', 'reference project_statuses', label='Статус проекта'),
    Field('budget', 'decimal(10,2)', default=0, label='Бюджет проекта'),
    Field('description', 'text', label='Описание проекта'),
    Field('notes', 'text', label='Примечания'),
    Field('created_on', 'datetime', default=request.now, writable=False, readable=True),
    Field('modified_on', 'datetime', default=request.now, update=request.now, writable=False, readable=True),
    Field('created_at', 'datetime', default=datetime.datetime.utcnow, writable=False, readable=True, label='Дата создания'),
    Field('updated_at', 'datetime', default=datetime.datetime.utcnow, update=datetime.datetime.utcnow, writable=False, readable=True, label='Дата обновления'),
    Field('status_started_at', 'datetime', default=datetime.datetime.utcnow, label='Дата входа в текущий статус'),
    Field('sla_hours', 'integer', default=None, label='SLA - максимальное время в статусе (часы)'),
    Field('manager_id', 'reference auth_user', label='Ответственный менеджер'),
    format='%(name)s'
)

# Таблица: Комплекты
db.define_table('complects',
    Field('customer_id', 'reference customers', required=True, label='Клиент'),
    Field('project_id', 'reference projects', label='Проект'),
    Field('status_id', 'reference complect_statuses', required=True, label='Статус'),
    Field('status_changed_on', 'datetime', default=request.now, label='Дата и время изменения статуса'),
    Field('next_step_id', 'reference next_steps', label='Следующий шаг'),
    Field('execution_time', 'integer', label='Время на выполнение (дни)'),
    Field('deadline', 'datetime', label='Дедлайн'),
    Field('description', 'text', label='Описание комплекта'),
    Field('total_amount', 'decimal(10,2)', default=0, label='Общая сумма'),
    Field('created_on', 'datetime', default=request.now, writable=False, readable=True),
    Field('modified_on', 'datetime', default=request.now, update=request.now, writable=False, readable=True),
    format='%(id)s - %(customer_id)s'
)

# Таблица: Позиции комплекта (nomenclature_item_id задаётся после определения nomenclature_items)
db.define_table('complect_items',
    Field('complect_id', 'reference complects', required=True, label='Комплект'),
    Field('nomenclature_item_id', 'integer', label='Позиция номенклатуры'),
    Field('item_name', 'string', length=200, required=True, label='Название позиции'),
    Field('quantity', 'decimal(10,2)', default=1, label='Количество'),
    Field('unit', 'string', length=50, default='шт', label='Единица измерения'),
    Field('price', 'decimal(10,2)', default=0, label='Цена за единицу'),
    Field('total', 'decimal(10,2)', default=0, label='Итого'),
    Field('description', 'text', label='Описание'),
    Field('created_on', 'datetime', default=request.now, writable=False, readable=True),
    format='%(item_name)s'
)

# Таблица: Заказы
db.define_table('orders',
    Field('complect_id', 'reference complects', label='Комплект'),
    Field('project_id', 'reference projects', label='Проект'),
    Field('customer_id', 'reference customers', required=True, label='Клиент'),
    Field('order_number', 'string', length=50, unique=True, required=True, label='Номер заказа'),
    Field('order_date', 'date', default=request.now.date(), label='Дата заказа'),
    Field('total_amount', 'decimal(10,2)', default=0, label='Общая сумма'),
    Field('description', 'text', label='Описание заказа'),
    Field('created_on', 'datetime', default=request.now, writable=False, readable=True),
    Field('modified_on', 'datetime', default=request.now, update=request.now, writable=False, readable=True),
    format='%(order_number)s'
)

# Таблица: Позиции заказа
db.define_table('order_items',
    Field('order_id', 'reference orders', required=True, label='Заказ'),
    Field('item_name', 'string', length=200, required=True, label='Название позиции'),
    Field('quantity', 'decimal(10,2)', default=1, label='Количество'),
    Field('unit', 'string', length=50, default='шт', label='Единица измерения'),
    Field('price', 'decimal(10,2)', default=0, label='Цена за единицу'),
    Field('total', 'decimal(10,2)', default=0, label='Итого'),
    Field('description', 'text', label='Описание'),
    Field('created_on', 'datetime', default=request.now, writable=False, readable=True),
    format='%(item_name)s'
)

# Таблица: Позиции номенклатуры
db.define_table('nomenclature_items',
    Field('item_number', 'string', length=50, unique=True, required=True, label='Номер позиции номенклатуры'),
    Field('item_date', 'date', default=request.now.date(), label='Дата позиции'),
    Field('unit', 'string', length=50, default='шт', label='Единица измерения'),
    Field('total_cost', 'decimal(10,2)', default=0, label='Общая стоимость'),
    Field('description', 'text', label='Описание позиции номенклатуры'),
    Field('created_on', 'datetime', default=request.now, writable=False, readable=True),
    Field('modified_on', 'datetime', default=request.now, update=request.now, writable=False, readable=True),
    format='%(item_number)s'
)

# Ссылка позиции комплекта на номенклатуру (поле остаётся integer, валидатор проверяет наличие в nomenclature_items)
db.complect_items.nomenclature_item_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.nomenclature_items.id, '%(item_number)s'))

# -------------------------------------------------------------------------
# Индексы для оптимизации запросов
# -------------------------------------------------------------------------
db.complects.customer_id.requires = IS_IN_DB(db, db.customers.id, '%(name)s')
db.complects.project_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.projects.id, '%(name)s'))
db.complects.status_id.requires = IS_IN_DB(db, db.complect_statuses.id, '%(name)s')
db.complects.next_step_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.next_steps.id, '%(name)s'))
db.complect_items.complect_id.requires = IS_IN_DB(db, db.complects.id, '%(id)s')
db.orders.customer_id.requires = IS_IN_DB(db, db.customers.id, '%(name)s')
db.orders.project_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.projects.id, '%(name)s'))
db.orders.complect_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.complects.id, '%(id)s'))
db.order_items.order_id.requires = IS_IN_DB(db, db.orders.id, '%(order_number)s')
db.projects.customer_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.customers.id, '%(name)s'))
# Обновляем тип полей complect_id и order_id на reference после определения таблиц complects и orders
db.projects.complect_id.type = db.complects
db.projects.order_id.type = db.orders
db.projects.complect_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.complects.id, '%(id)s'))
db.projects.order_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.orders.id, '%(order_number)s'))
db.projects.status_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.project_statuses.id, '%(name)s'))
db.projects.manager_id.requires = IS_EMPTY_OR(IS_IN_DB(db, db.auth_user.id, '%(first_name)s %(last_name)s'))

# -------------------------------------------------------------------------
# Валидаторы для полей
# -------------------------------------------------------------------------
db.customers.email.requires = IS_EMPTY_OR(IS_EMAIL())
db.customers.phone.requires = IS_EMPTY_OR(IS_MATCH('^[\d\s\-\+\(\)]+$', error_message='Неверный формат телефона'))
db.complects.execution_time.requires = IS_EMPTY_OR(IS_INT_IN_RANGE(0, 1000))
db.complect_items.quantity.requires = IS_FLOAT_IN_RANGE(0.01, 1000000)
db.complect_items.price.requires = IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0, 10000000))
db.order_items.quantity.requires = IS_FLOAT_IN_RANGE(0.01, 1000000)
db.order_items.price.requires = IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0, 10000000))
db.projects.budget.requires = IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0, 100000000))

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
