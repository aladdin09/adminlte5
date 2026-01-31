# -*- coding: utf-8 -*-
"""
Сервисный слой для работы с таблицей customers (Клиенты)
"""


def create_customer(db, name, phone=None, email=None, address=None, notes=None):
    """
    Создать нового клиента
    
    Args:
        db: объект базы данных
        name: имя клиента
        phone: телефон
        email: email
        address: адрес
        notes: примечания
    
    Returns:
        dict: результат операции {'success': bool, 'id': int, 'error': str}
    """
    try:
        customer_id = db.customers.insert(
            name=name,
            phone=phone,
            email=email,
            address=address,
            notes=notes
        )
        db.commit()
        return {'success': True, 'id': customer_id}
    except Exception as e:
        db.rollback()
        return {'success': False, 'error': str(e)}


def get_customer_by_id(db, customer_id):
    """
    Получить клиента по ID
    
    Args:
        db: объект базы данных
        customer_id: ID клиента
    
    Returns:
        Row или None: запись клиента или None если не найдена
    """
    try:
        return db.customers(customer_id) or None
    except Exception as e:
        return None


def get_all_customers(db, order_by='name', limitby=None):
    """
    Получить всех клиентов
    
    Args:
        db: объект базы данных
        order_by: поле для сортировки
        limitby: ограничение количества (start, end)
    
    Returns:
        Rows: список всех клиентов
    """
    try:
        query = db.customers.id > 0
        if limitby:
            return db(query).select(orderby=db.customers[order_by], limitby=limitby)
        return db(query).select(orderby=db.customers[order_by])
    except Exception as e:
        return db().select(db.customers.id)


def update_customer(db, customer_id, **kwargs):
    """
    Обновить клиента
    
    Args:
        db: объект базы данных
        customer_id: ID клиента
        **kwargs: поля для обновления (name, phone, email, address, notes)
    
    Returns:
        dict: результат операции {'success': bool, 'error': str}
    """
    try:
        customer = db.customers(customer_id)
        if not customer:
            return {'success': False, 'error': 'Клиент не найден'}
        
        allowed_fields = ['name', 'phone', 'email', 'address', 'notes']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if update_data:
            db(db.customers.id == customer_id).update(**update_data)
            db.commit()
        return {'success': True}
    except Exception as e:
        db.rollback()
        return {'success': False, 'error': str(e)}


def delete_customer(db, customer_id):
    """
    Удалить клиента
    
    Args:
        db: объект базы данных
        customer_id: ID клиента
    
    Returns:
        dict: результат операции {'success': bool, 'error': str}
    """
    try:
        customer = db.customers(customer_id)
        if not customer:
            return {'success': False, 'error': 'Клиент не найден'}
        
        db(db.customers.id == customer_id).delete()
        db.commit()
        return {'success': True}
    except Exception as e:
        db.rollback()
        return {'success': False, 'error': str(e)}


def search_customers(db, search_term, order_by='name'):
    """
    Поиск клиентов по имени, телефону, email или адресу
    
    Args:
        db: объект базы данных
        search_term: поисковый запрос
        order_by: поле для сортировки
    
    Returns:
        Rows: список найденных клиентов
    """
    try:
        query = (db.customers.name.contains(search_term)) | \
                (db.customers.phone.contains(search_term)) | \
                (db.customers.email.contains(search_term)) | \
                (db.customers.address.contains(search_term))
        return db(query).select(orderby=db.customers[order_by])
    except Exception as e:
        return db().select(db.customers.id)


def get_customer_complects(db, customer_id):
    """
    Получить все комплекты клиента
    """
    try:
        return db(db.complects.customer_id == customer_id).select(
            orderby=~db.complects.created_on
        )
    except Exception as e:
        return db().select(db.complects.id)
