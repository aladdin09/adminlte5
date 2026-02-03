# -*- coding: utf-8 -*-
"""
Контроллер для работы со спецификациями
"""
from gluon.http import HTTP
import role_helpers


def get_status_color(status_name):
    """Возвращает цвет для статуса"""
    colors = {
        'Лид': 'primary',
        'Спецификация': 'info',
        'Коммерческое предложение': 'warning',
        'Заказ': 'success',
        'Производство': 'danger'
    }
    return colors.get(status_name, 'secondary')


def view_specification():
    """Карточка спецификации"""
    specification_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import specifications_service
        import specification_items_service
        specification = specifications_service.get_specification_by_id(db, specification_id)
        if not specification:
            session.flash = 'Спецификация не найдена'
            redirect(URL('default', 'index'))
        # Менеджер видит только спецификации своих проектов/клиентов
        if role_helpers.is_manager(auth):
            if specification.project_id:
                if specification.project_id not in role_helpers.get_manager_project_ids(db, auth.user.id):
                    raise HTTP(403, 'Доступ запрещён: вы можете видеть только свои спецификации.')
            else:
                if specification.customer_id not in role_helpers.get_manager_customer_ids(db, auth.user.id):
                    raise HTTP(403, 'Доступ запрещён: вы можете видеть только свои спецификации.')
        import customers_service
        customer = customers_service.get_customer_by_id(db, specification.customer_id)
        import specification_statuses_service
        status = specification_statuses_service.get_status_by_id(db, specification.status_id)
        next_step = None
        if specification.next_step_id:
            import next_steps_service
            next_step = next_steps_service.get_next_step_by_id(db, specification.next_step_id)
        specification_items = specification_items_service.get_all_specification_items(db, specification_id=specification_id)
        all_statuses = specification_statuses_service.get_all_statuses(db, is_active=True, order_by='sort_order')
        import next_steps_service
        all_next_steps = next_steps_service.get_all_next_steps(db, is_active=True)
        status_colors = {}
        if status:
            status_colors[status.id] = get_status_color(status.name)
        nomenclature_items = db(db.nomenclature_items.id > 0).select(orderby=db.nomenclature_items.item_number)
        # Хлебные крошки: Главная → Клиенты → Клиент [→ Проект] → Спецификация
        import breadcrumbs_helper
        project = None
        if specification.project_id:
            import projects_service
            project = projects_service.get_project_by_id(db, specification.project_id)
        if customer:
            items = [
                ('Главная', URL('default', 'index')),
                ('Клиенты', URL('customers', 'customers_list')),
                (customer.name, URL('customers', 'customer', args=[customer.id])),
            ]
            if project:
                items.append((project.name or project.project_number or 'Проект', URL('projects', 'view', args=[project.id])))
            items.append(('Спецификация #%s' % specification.id, None))
        else:
            items = [
                ('Главная', URL('default', 'index')),
                ('Спецификация #%s' % specification.id, None),
            ]
        breadcrumbs = breadcrumbs_helper.make_breadcrumbs(items)
        return dict(
            specification_obj=specification,
            customer=customer,
            project=project,
            status=status,
            next_step=next_step,
            specification_items=specification_items,
            all_statuses=all_statuses,
            all_next_steps=all_next_steps,
            status_colors=status_colors,
            nomenclature_items=nomenclature_items,
            breadcrumbs=breadcrumbs,
        )
    except Exception as e:
        session.flash = f'Ошибка: {str(e)}'
        redirect(URL('default', 'index'))


def add_specification():
    """Добавление новой спецификации для клиента"""
    customer_id = request.args(0)
    if not customer_id:
        session.flash = 'Не указан ID клиента'
        redirect(URL('default', 'index'))
    try:
        from gluon.http import HTTP
        import customers_service
        import specifications_service
        import specification_statuses_service
        customer = customers_service.get_customer_by_id(db, customer_id)
        if not customer:
            session.flash = 'Клиент не найден'
            redirect(URL('default', 'index'))
        # Менеджер может добавлять спецификации только своим клиентам
        if role_helpers.is_manager(auth) and int(customer_id) not in role_helpers.get_manager_customer_ids(db, auth.user.id):
            raise HTTP(403, 'Доступ запрещён: вы можете работать только со своими клиентами.')
        all_statuses = specification_statuses_service.get_all_statuses(db, is_active=True, order_by='sort_order')
        if not all_statuses:
            session.flash = 'Нет доступных статусов. Создайте статусы в системе.'
            redirect(URL('customers', 'customer', args=[customer_id]))
        first_status = all_statuses.first()
        if not first_status:
            session.flash = 'Не удалось получить статус по умолчанию'
            redirect(URL('customers', 'customer', args=[customer_id]))
        default_status_id = first_status.id
        result = specifications_service.create_specification(
            db,
            customer_id=customer_id,
            status_id=default_status_id,
            description='Новая спецификация',
            total_amount=0
        )
        if result.get('success'):
            specification_id = result.get('id')
            if specification_id:
                session.flash = 'Спецификация успешно создана'
                redirect(URL('specifications', 'view_specification', args=[specification_id], vars={}))
            else:
                session.flash = 'Ошибка: не получен ID созданной спецификации'
                redirect(URL('customers', 'customer', args=[customer_id]))
        else:
            session.flash = f'Ошибка при создании спецификации: {result.get("error", "Неизвестная ошибка")}'
            redirect(URL('customers', 'customer', args=[customer_id]))
    except HTTP:
        raise
    except Exception as e:
        db.rollback()
        session.flash = f'Ошибка при создании спецификации: {str(e)}'
        if 'customer_id' in locals():
            redirect(URL('customers', 'customer', args=[customer_id]))
        else:
            redirect(URL('default', 'index'))


def add_items_from_nomenclature():
    """Добавить в спецификацию позиции по выбранным позициям номенклатуры (POST: nomenclature_item_ids, specification_id в args)."""
    specification_id = request.args(0) or redirect(URL('default', 'index'))
    if request.env.request_method != 'POST':
        redirect(URL('specifications', 'view_specification', args=[specification_id]))
    try:
        import importlib
        import specification_items_service
        importlib.reload(specification_items_service)
        import specifications_service
        specification = specifications_service.get_specification_by_id(db, specification_id)
        if not specification:
            session.flash = 'Спецификация не найдена'
            redirect(URL('default', 'index'))
        nomenclature_item_ids = request.post_vars.get('nomenclature_item_ids')
        if nomenclature_item_ids is None:
            nomenclature_item_ids = []
        elif isinstance(nomenclature_item_ids, str):
            s = nomenclature_item_ids.strip()
            nomenclature_item_ids = [x.strip() for x in s.split(',') if x.strip()]
        elif not isinstance(nomenclature_item_ids, list):
            nomenclature_item_ids = [nomenclature_item_ids] if nomenclature_item_ids else []
        specification_id = int(specification_id)
        result = specification_items_service.create_specification_items_from_nomenclature(db, specification_id, nomenclature_item_ids)
        if result.get('success'):
            added = result.get('added', 0)
            session.flash = 'Добавлено позиций: %s' % added if added else 'Выберите позиции номенклатуры'
        else:
            session.flash = 'Ошибка при добавлении: %s' % (result.get('error') or 'неизвестная ошибка')
        redirect(URL('specifications', 'view_specification', args=[specification_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('specifications', 'view_specification', args=[specification_id]))


def delete_item():
    """Удалить позицию спецификации. args: [item_id]. Редирект на карточку спецификации."""
    item_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import specification_items_service
        item = specification_items_service.get_specification_item_by_id(db, item_id)
        if not item:
            session.flash = 'Позиция не найдена'
            redirect(URL('default', 'index'))
        specification_id = item.specification_id
        result = specification_items_service.delete_specification_item(db, item_id)
        if result.get('success'):
            session.flash = 'Позиция удалена'
        else:
            session.flash = 'Ошибка при удалении: %s' % (result.get('error') or '')
        redirect(URL('specifications', 'view_specification', args=[specification_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


# ID статусов спецификации для кнопок на карточке проекта
SPECIFICATION_STATUS_ROP_ID = 2            # На согласовании у РОПа
SPECIFICATION_STATUS_ISPRAVLENIE_ID = 3    # Исправление
SPECIFICATION_STATUS_KP_SOGLASOVANO_ID = 4 # КП согласовано
SPECIFICATION_STATUS_KP_OTPRAVLENO_ID = 5  # КП отправлено
SPECIFICATION_STATUS_ZAKAZ_ID = 6          # Заказ


# ID статусов проекта при действиях со спецификацией
PROJECT_STATUS_KP_U_ROPA_ID = 3       # КП у РОПа — при «На согласование РОПу»
PROJECT_STATUS_ISPRAVLENIE_KP_ID = 4  # Исправление КП — при «Исправить»
PROJECT_STATUS_KP_SOGLASOVANO_ID = 5 # КП согласовано — при «Согласовать КП»
PROJECT_STATUS_KP_OTPRAVLENO_ID = 6  # КП отправлено — при «КП отправлено»
PROJECT_STATUS_ZAKAZ_OFORMLEN_ID = 7 # Заказ оформлен — при «Создать заказ»


def set_status_rop():
    """Перевести спецификацию в статус «На согласовании у РОПа» (id=2), проект — в «КП у РОПа» (id=3). args: [specification_id]."""
    specification_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import specifications_service
        specification = specifications_service.get_specification_by_id(db, specification_id)
        if not specification:
            session.flash = 'Спецификация не найдена'
            redirect(URL('default', 'index'))
        project_id = specification.project_id
        result = specifications_service.update_specification_status(db, specification_id, SPECIFICATION_STATUS_ROP_ID)
        if result.get('success'):
            session.flash = 'Статус спецификации изменён на «На согласовании у РОПа»'
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
            redirect(URL('specifications', 'view_specification', args=[specification_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_ispravlenie():
    """Перевести спецификацию в статус «Исправление» (id=3), проект — в «Исправление КП» (id=4). args: [specification_id]."""
    specification_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import specifications_service
        specification = specifications_service.get_specification_by_id(db, specification_id)
        if not specification:
            session.flash = 'Спецификация не найдена'
            redirect(URL('default', 'index'))
        project_id = specification.project_id
        result = specifications_service.update_specification_status(db, specification_id, SPECIFICATION_STATUS_ISPRAVLENIE_ID)
        if result.get('success'):
            session.flash = 'Статус спецификации изменён на «Исправление»'
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
            redirect(URL('specifications', 'view_specification', args=[specification_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_kp_soglasovano():
    """Перевести спецификацию в статус «КП согласовано» (id=4), проект — в «КП согласовано» (id=5). args: [specification_id]."""
    specification_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import specifications_service
        specification = specifications_service.get_specification_by_id(db, specification_id)
        if not specification:
            session.flash = 'Спецификация не найдена'
            redirect(URL('default', 'index'))
        project_id = specification.project_id
        result = specifications_service.update_specification_status(db, specification_id, SPECIFICATION_STATUS_KP_SOGLASOVANO_ID)
        if result.get('success'):
            session.flash = 'Статус спецификации изменён на «КП согласовано»'
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
            redirect(URL('specifications', 'view_specification', args=[specification_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_kp_otpravleno():
    """Перевести спецификацию в статус «КП отправлено» (id=5), проект — в «КП отправлено» (id=6). args: [specification_id]."""
    specification_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import specifications_service
        specification = specifications_service.get_specification_by_id(db, specification_id)
        if not specification:
            session.flash = 'Спецификация не найдена'
            redirect(URL('default', 'index'))
        project_id = specification.project_id
        result = specifications_service.update_specification_status(db, specification_id, SPECIFICATION_STATUS_KP_OTPRAVLENO_ID)
        if result.get('success'):
            session.flash = 'Статус спецификации изменён на «КП отправлено»'
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
            redirect(URL('specifications', 'view_specification', args=[specification_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_chernovik():
    """Перевести спецификацию в статус «Черновик». args: [specification_id]."""
    specification_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import specifications_service
        specification = specifications_service.get_specification_by_id(db, specification_id)
        if not specification:
            session.flash = 'Спецификация не найдена'
            redirect(URL('default', 'index'))
        project_id = specification.project_id
        chernovik = db(db.specification_statuses.name == 'Черновик').select().first()
        if not chernovik:
            session.flash = 'Статус «Черновик» не найден в справочнике'
            if project_id:
                redirect(URL('projects', 'view', args=[project_id]))
            else:
                redirect(URL('specifications', 'view_specification', args=[specification_id]))
        result = specifications_service.update_specification_status(db, specification_id, chernovik.id)
        if result.get('success'):
            session.flash = 'Статус спецификации изменён на «Черновик»'
        else:
            session.flash = 'Ошибка: %s' % (result.get('error') or '')
        if project_id:
            redirect(URL('projects', 'view', args=[project_id]))
        else:
            redirect(URL('specifications', 'view_specification', args=[specification_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))


def set_status_zakaz():
    """Создать заказ из спецификации (копирование в orders и order_items), перевести спецификацию в статус «Заказ» (id=6). args: [specification_id]."""
    specification_id = request.args(0) or redirect(URL('default', 'index'))
    try:
        import specifications_service
        import orders_service
        specification = specifications_service.get_specification_by_id(db, specification_id)
        if not specification:
            session.flash = 'Спецификация не найдена'
            redirect(URL('default', 'index'))
        project_id = specification.project_id
        result = orders_service.create_order_from_specification(db, specification_id)
        if not result.get('success'):
            session.flash = 'Ошибка при создании заказа: %s' % (result.get('error') or '')
            if project_id:
                redirect(URL('projects', 'view', args=[project_id]))
            else:
                redirect(URL('specifications', 'view_specification', args=[specification_id]))
        order_id = result.get('id')
        specifications_service.update_specification_status(db, specification_id, SPECIFICATION_STATUS_ZAKAZ_ID)
        if project_id:
            import projects_service
            projects_service.update_project_status(db, int(project_id), PROJECT_STATUS_ZAKAZ_OFORMLEN_ID)
        session.flash = 'Заказ создан из спецификации'
        redirect(URL('orders', 'view', args=[order_id]))
    except HTTP:
        raise
    except Exception as e:
        session.flash = 'Ошибка: %s' % str(e)
        redirect(URL('default', 'index'))
