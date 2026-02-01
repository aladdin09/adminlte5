# -*- coding: utf-8 -*-
"""
Контроллер для работы с комплектами
"""
from gluon.http import HTTP


def get_status_color(status_name):
    """Возвращает цвет для статуса"""
    colors = {
        'Лид': 'primary',
        'Комплект': 'info',
        'Коммерческое предложение': 'warning',
        'Заказ': 'success',
        'Производство': 'danger'
    }
    return colors.get(status_name, 'secondary')


def view_complect():
    """Карточка комплекта"""
    complect_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import complects_service
        import complect_items_service
        complect = complects_service.get_complect_by_id(db, complect_id)
        if not complect:
            session.flash = 'Комплект не найден'
            redirect(URL('default', 'index'))
        import customers_service
        customer = customers_service.get_customer_by_id(db, complect.customer_id)
        import complect_statuses_service
        status = complect_statuses_service.get_status_by_id(db, complect.status_id)
        next_step = None
        if complect.next_step_id:
            import next_steps_service
            next_step = next_steps_service.get_next_step_by_id(db, complect.next_step_id)
        complect_items = complect_items_service.get_all_complect_items(db, complect_id=complect_id)
        all_statuses = complect_statuses_service.get_all_statuses(db, is_active=True, order_by='sort_order')
        import next_steps_service
        all_next_steps = next_steps_service.get_all_next_steps(db, is_active=True)
        status_colors = {}
        if status:
            status_colors[status.id] = get_status_color(status.name)
        nomenclature_items = db(db.nomenclature_items.id > 0).select(orderby=db.nomenclature_items.item_number)
        # Хлебные крошки: Главная → Клиенты → Клиент [→ Проект] → Комплект
        import breadcrumbs_helper
        project = None
        if complect.project_id:
            import projects_service
            project = projects_service.get_project_by_id(db, complect.project_id)
        if customer:
            items = [
                ('Главная', URL('default', 'index')),
                ('Клиенты', URL('customers', 'customers_list')),
                (customer.name, URL('customers', 'customer', args=[customer.id])),
            ]
            if project:
                items.append((project.name or project.project_number or 'Проект', URL('projects', 'view', args=[project.id])))
            items.append(('Комплект #%s' % complect.id, None))
        else:
            items = [
                ('Главная', URL('default', 'index')),
                ('Комплект #%s' % complect.id, None),
            ]
        breadcrumbs = breadcrumbs_helper.make_breadcrumbs(items)
        return dict(
            complect_obj=complect,
            customer=customer,
            project=project,
            status=status,
            next_step=next_step,
            complect_items=complect_items,
            all_statuses=all_statuses,
            all_next_steps=all_next_steps,
            status_colors=status_colors,
            nomenclature_items=nomenclature_items,
            breadcrumbs=breadcrumbs,
        )
    except Exception as e:
        session.flash = f'Ошибка: {str(e)}'
        redirect(URL('default', 'index'))


def add_complect():
    """Добавление нового комплекта для клиента"""
    customer_id = request.args(0)
    if not customer_id:
        session.flash = 'Не указан ID клиента'
        redirect(URL('default', 'index'))
    try:
        from gluon.http import HTTP
        import customers_service
        import complects_service
        import complect_statuses_service
        customer = customers_service.get_customer_by_id(db, customer_id)
        if not customer:
            session.flash = 'Клиент не найден'
            redirect(URL('default', 'index'))
        all_statuses = complect_statuses_service.get_all_statuses(db, is_active=True, order_by='sort_order')
        if not all_statuses:
            session.flash = 'Нет доступных статусов. Создайте статусы в системе.'
            redirect(URL('customers', 'customer', args=[customer_id]))
        first_status = all_statuses.first()
        if not first_status:
            session.flash = 'Не удалось получить статус по умолчанию'
            redirect(URL('customers', 'customer', args=[customer_id]))
        default_status_id = first_status.id
        result = complects_service.create_complect(
            db,
            customer_id=customer_id,
            status_id=default_status_id,
            description='Новый комплект',
            total_amount=0
        )
        if result.get('success'):
            complect_id = result.get('id')
            if complect_id:
                session.flash = 'Комплект успешно создан'
                redirect(URL('complects', 'view_complect', args=[complect_id], vars={}))
            else:
                session.flash = 'Ошибка: не получен ID созданного комплекта'
                redirect(URL('customers', 'customer', args=[customer_id]))
        else:
            session.flash = f'Ошибка при создании комплекта: {result.get("error", "Неизвестная ошибка")}'
            redirect(URL('customers', 'customer', args=[customer_id]))
    except HTTP:
        raise
    except Exception as e:
        db.rollback()
        session.flash = f'Ошибка при создании комплекта: {str(e)}'
        if 'customer_id' in locals():
            redirect(URL('customers', 'customer', args=[customer_id]))
        else:
            redirect(URL('default', 'index'))


def add_items_from_nomenclature():
    """Добавить в комплект позиции по выбранным позициям номенклатуры (POST: nomenclature_item_ids, complect_id в args)."""
    complect_id = request.args(0) or redirect(URL('default', 'index'))
    if request.env.request_method != 'POST':
        redirect(URL('complects', 'view_complect', args=[complect_id]))
    try:
        import importlib
        import complect_items_service
        importlib.reload(complect_items_service)
        import complects_service
        complect = complects_service.get_complect_by_id(db, complect_id)
        if not complect:
            session.flash = 'Комплект не найден'
            redirect(URL('default', 'index'))
        nomenclature_item_ids = request.post_vars.get('nomenclature_item_ids')
        if nomenclature_item_ids is None:
            nomenclature_item_ids = []
        elif isinstance(nomenclature_item_ids, str):
            s = nomenclature_item_ids.strip()
            nomenclature_item_ids = [x.strip() for x in s.split(',') if x.strip()]
        elif not isinstance(nomenclature_item_ids, list):
            nomenclature_item_ids = [nomenclature_item_ids] if nomenclature_item_ids else []
        complect_id = int(complect_id)
        result = complect_items_service.create_complect_items_from_nomenclature(db, complect_id, nomenclature_item_ids)
        if result.get('success'):
            added = result.get('added', 0)
            session.flash = 'Добавлено позиций: %s' % added if added else 'Выберите позиции номенклатуры'
        else:
            session.flash = 'Ошибка при добавлении: %s' % (result.get('error') or 'неизвестная ошибка')
        redirect(URL('complects', 'view_complect', args=[complect_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('complects', 'view_complect', args=[complect_id]))


def delete_item():
    """Удалить позицию комплекта. args: [item_id]. Редирект на карточку комплекта."""
    item_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import complect_items_service
        item = complect_items_service.get_complect_item_by_id(db, item_id)
        if not item:
            session.flash = 'Позиция не найдена'
            redirect(URL('default', 'index'))
        complect_id = item.complect_id
        result = complect_items_service.delete_complect_item(db, item_id)
        if result.get('success'):
            session.flash = 'Позиция удалена'
        else:
            session.flash = 'Ошибка при удалении: %s' % (result.get('error') or '')
        redirect(URL('complects', 'view_complect', args=[complect_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


# ID статусов комплекта для кнопок на карточке проекта
COMPLECT_STATUS_ROP_ID = 2            # На согласовании у РОПа
COMPLECT_STATUS_ISPRAVLENIE_ID = 3    # Исправление
COMPLECT_STATUS_KP_SOGLASOVANO_ID = 4 # КП согласовано
COMPLECT_STATUS_KP_OTPRAVLENO_ID = 5  # КП отправлено
COMPLECT_STATUS_ZAKAZ_ID = 6          # Заказ


# ID статусов проекта при действиях с комплектом
PROJECT_STATUS_KP_U_ROPA_ID = 3       # КП у РОПа — при «На согласование РОПу»
PROJECT_STATUS_ISPRAVLENIE_KP_ID = 4  # Исправление КП — при «Исправить»
PROJECT_STATUS_KP_SOGLASOVANO_ID = 5 # КП согласовано — при «Согласовать КП»
PROJECT_STATUS_KP_OTPRAVLENO_ID = 6  # КП отправлено — при «КП отправлено»
PROJECT_STATUS_ZAKAZ_OFORMLEN_ID = 7 # Заказ оформлен — при «Создать заказ»


def set_status_rop():
    """Перевести комплект в статус «На согласовании у РОПа» (id=2), проект — в «КП у РОПа» (id=3). args: [complect_id]."""
    complect_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import complects_service
        complect = complects_service.get_complect_by_id(db, complect_id)
        if not complect:
            session.flash = 'Комплект не найден'
            redirect(URL('default', 'index'))
        project_id = complect.project_id
        result = complects_service.update_complect_status(db, complect_id, COMPLECT_STATUS_ROP_ID)
        if result.get('success'):
            session.flash = 'Статус комплекта изменён на «На согласовании у РОПа»'
            if project_id:
                import projects_service
                upd = projects_service.update_project_status(db, int(project_id), PROJECT_STATUS_KP_U_ROPA_ID)
                if not upd.get('success'):
                    session.flash += '. Статус проекта не обновлён: %s' % (upd.get('error') or '')
        else:
            session.flash = 'Ошибка: %s' % (result.get('error') or '')
        if project_id:
            redirect(URL('projects', 'view', args=[project_id]))
        else:
            redirect(URL('complects', 'view_complect', args=[complect_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_ispravlenie():
    """Перевести комплект в статус «Исправление» (id=3), проект — в «Исправление КП» (id=4). args: [complect_id]."""
    complect_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import complects_service
        complect = complects_service.get_complect_by_id(db, complect_id)
        if not complect:
            session.flash = 'Комплект не найден'
            redirect(URL('default', 'index'))
        project_id = complect.project_id
        result = complects_service.update_complect_status(db, complect_id, COMPLECT_STATUS_ISPRAVLENIE_ID)
        if result.get('success'):
            session.flash = 'Статус комплекта изменён на «Исправление»'
            if project_id:
                import projects_service
                upd = projects_service.update_project_status(db, int(project_id), PROJECT_STATUS_ISPRAVLENIE_KP_ID)
                if not upd.get('success'):
                    session.flash += '. Статус проекта не обновлён: %s' % (upd.get('error') or '')
        else:
            session.flash = 'Ошибка: %s' % (result.get('error') or '')
        if project_id:
            redirect(URL('projects', 'view', args=[project_id]))
        else:
            redirect(URL('complects', 'view_complect', args=[complect_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_kp_soglasovano():
    """Перевести комплект в статус «КП согласовано» (id=4), проект — в «КП согласовано» (id=5). args: [complect_id]."""
    complect_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import complects_service
        complect = complects_service.get_complect_by_id(db, complect_id)
        if not complect:
            session.flash = 'Комплект не найден'
            redirect(URL('default', 'index'))
        project_id = complect.project_id
        result = complects_service.update_complect_status(db, complect_id, COMPLECT_STATUS_KP_SOGLASOVANO_ID)
        if result.get('success'):
            session.flash = 'Статус комплекта изменён на «КП согласовано»'
            if project_id:
                import projects_service
                upd = projects_service.update_project_status(db, int(project_id), PROJECT_STATUS_KP_SOGLASOVANO_ID)
                if not upd.get('success'):
                    session.flash += '. Статус проекта не обновлён: %s' % (upd.get('error') or '')
        else:
            session.flash = 'Ошибка: %s' % (result.get('error') or '')
        if project_id:
            redirect(URL('projects', 'view', args=[project_id]))
        else:
            redirect(URL('complects', 'view_complect', args=[complect_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_kp_otpravleno():
    """Перевести комплект в статус «КП отправлено» (id=5), проект — в «КП отправлено» (id=6). args: [complect_id]."""
    complect_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import complects_service
        complect = complects_service.get_complect_by_id(db, complect_id)
        if not complect:
            session.flash = 'Комплект не найден'
            redirect(URL('default', 'index'))
        project_id = complect.project_id
        result = complects_service.update_complect_status(db, complect_id, COMPLECT_STATUS_KP_OTPRAVLENO_ID)
        if result.get('success'):
            session.flash = 'Статус комплекта изменён на «КП отправлено»'
            if project_id:
                import projects_service
                upd = projects_service.update_project_status(db, int(project_id), PROJECT_STATUS_KP_OTPRAVLENO_ID)
                if not upd.get('success'):
                    session.flash += '. Статус проекта не обновлён: %s' % (upd.get('error') or '')
        else:
            session.flash = 'Ошибка: %s' % (result.get('error') or '')
        if project_id:
            redirect(URL('projects', 'view', args=[project_id]))
        else:
            redirect(URL('complects', 'view_complect', args=[complect_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_chernovik():
    """Перевести комплект в статус «Черновик». args: [complect_id]."""
    complect_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import complects_service
        complect = complects_service.get_complect_by_id(db, complect_id)
        if not complect:
            session.flash = 'Комплект не найден'
            redirect(URL('default', 'index'))
        project_id = complect.project_id
        chernovik = db(db.complect_statuses.name == 'Черновик').select().first()
        if not chernovik:
            session.flash = 'Статус «Черновик» не найден в справочнике'
            if project_id:
                redirect(URL('projects', 'view', args=[project_id]))
            else:
                redirect(URL('complects', 'view_complect', args=[complect_id]))
        result = complects_service.update_complect_status(db, complect_id, chernovik.id)
        if result.get('success'):
            session.flash = 'Статус комплекта изменён на «Черновик»'
        else:
            session.flash = 'Ошибка: %s' % (result.get('error') or '')
        if project_id:
            redirect(URL('projects', 'view', args=[project_id]))
        else:
            redirect(URL('complects', 'view_complect', args=[complect_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_zakaz():
    """Создать заказ из комплекта (копирование в orders и order_items), перевести комплект в статус «Заказ» (id=6). args: [complect_id]."""
    complect_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import complects_service
        import orders_service
        complect = complects_service.get_complect_by_id(db, complect_id)
        if not complect:
            session.flash = 'Комплект не найден'
            redirect(URL('default', 'index'))
        project_id = complect.project_id
        result = orders_service.create_order_from_complect(db, complect_id)
        if not result.get('success'):
            session.flash = 'Ошибка при создании заказа: %s' % (result.get('error') or '')
            if project_id:
                redirect(URL('projects', 'view', args=[project_id]))
            else:
                redirect(URL('complects', 'view_complect', args=[complect_id]))
        order_id = result.get('id')
        complects_service.update_complect_status(db, complect_id, COMPLECT_STATUS_ZAKAZ_ID)
        if project_id:
            import projects_service
            projects_service.update_project_status(db, int(project_id), PROJECT_STATUS_ZAKAZ_OFORMLEN_ID)
        session.flash = 'Заказ создан из комплекта'
        redirect(URL('orders', 'view', args=[order_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


