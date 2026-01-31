# -*- coding: utf-8 -*-
"""
Контроллер для работы с проектами
"""


def view():
    """
    Карточка проекта
    """
    raw_id = request.args(0)
    if not raw_id:
        session.flash = 'Не указан ID проекта'
        redirect(URL('default', 'index'))
    try:
        project_id = int(raw_id)
    except (TypeError, ValueError):
        session.flash = 'Неверный ID проекта'
        redirect(URL('default', 'index'))
    
    try:
        from gluon.http import HTTP
        import breadcrumbs_helper
        import projects_service
        import customers_service
        import project_statuses_service
        
        # Получаем проект (явный запрос по id)
        try:
            project = db(db.projects.id == project_id).select().first()
        except Exception as db_err:
            session.flash = 'Ошибка БД при загрузке проекта: %s' % str(db_err)
            redirect(URL('default', 'index'))
        if not project:
            session.flash = 'Проект с ID %s не найден в базе.' % project_id
            redirect(URL('default', 'index'))
        
        # Получаем клиента
        customer = None
        if project.customer_id:
            customer = customers_service.get_customer_by_id(db, project.customer_id)
        
        # Получаем статус проекта
        status = None
        if project.status_id:
            status = project_statuses_service.get_status_by_id(db, project.status_id)
        
        # Получаем комплекты проекта
        complects = db(db.complects.project_id == project_id).select(
            db.complects.ALL,
            db.complect_statuses.ALL,
            left=db.complect_statuses.on(db.complects.status_id == db.complect_statuses.id),
            orderby=~db.complects.created_on
        )
        
        # Получаем заказы проекта
        orders = db(db.orders.project_id == project_id).select(
            db.orders.ALL,
            orderby=~db.orders.created_on
        )
        
        # Получаем цвета статусов для отображения
        status_colors = {}
        if status:
            status_colors[status.id] = get_status_color(status.name)
        
        # Получаем цвета статусов комплектов
        complect_status_colors = {}
        import complect_statuses_service
        all_complect_statuses = complect_statuses_service.get_all_statuses(db, is_active=True, order_by='sort_order')
        for comp_status in all_complect_statuses:
            complect_status_colors[comp_status.id] = get_complect_status_color(comp_status.name)
        
        # Форма для добавления комплекта (для sidebar)
        form_complect = SQLFORM.factory(
            Field('description', 'text', label='Описание комплекта'),
            Field('execution_time', 'integer', label='Время на выполнение (дни)'),
            Field('deadline', 'datetime', label='Дедлайн'),
            Field('total_amount', 'decimal(10,2)', default=0, label='Общая сумма'),
            submit_button='Добавить',
            _id='complectForm',
            _name='complect_form',
            _action=URL('projects', 'view', args=[project_id]),
            _method='POST'
        )
        
        # Обработка формы добавления комплекта
        show_complect_panel = False
        if form_complect.process(formname='complect_form', keepvalues=False).accepted:
            description = str(form_complect.vars.description) if form_complect.vars.description else None
            try:
                execution_time = int(form_complect.vars.execution_time) if form_complect.vars.execution_time else None
            except:
                execution_time = None
            deadline = form_complect.vars.deadline if form_complect.vars.deadline else None
            try:
                total_amount = float(form_complect.vars.total_amount) if form_complect.vars.total_amount else 0
            except:
                total_amount = 0
            if not all_complect_statuses:
                session.flash = 'Нет доступных статусов комплектов. Создайте статусы в системе.'
                show_complect_panel = True
            else:
                first_status = all_complect_statuses.first()
                default_status_id = first_status.id if first_status else None
                if not default_status_id:
                    session.flash = 'Не удалось получить статус по умолчанию'
                    show_complect_panel = True
                else:
                    customer_id_for_complect = project.customer_id if project.customer_id else None
                    if not customer_id_for_complect:
                        session.flash = 'У проекта не указан клиент. Невозможно создать комплект.'
                        show_complect_panel = True
                    else:
                        import complects_service
                        import projects_service
                        import project_statuses_service
                        result = complects_service.create_complect(
                            db=db,
                            customer_id=customer_id_for_complect,
                            project_id=int(project_id),
                            status_id=default_status_id,
                            description=description or 'Новый комплект',
                            execution_time=execution_time,
                            deadline=deadline,
                            total_amount=total_amount
                        )
                        if result.get('success'):
                            # Первый комплект у проекта — переводим статус проекта в «Комплектация»
                            pid = int(project_id)
                            count = db(db.complects.project_id == pid).count()
                            if count == 1:
                                status_row = project_statuses_service.get_status_by_name(db, 'Комплектация')
                                status_complectation_id = status_row.id if status_row else 2  # запас: id=2
                                upd = projects_service.update_project_status(db, pid, status_complectation_id)
                                if not upd.get('success'):
                                    session.flash = 'Комплект добавлен, но статус проекта не обновлён: %s' % upd.get('error', '')
                                else:
                                    session.flash = 'Комплект успешно добавлен'
                            else:
                                session.flash = 'Комплект успешно добавлен'
                            redirect(URL('projects', 'view', args=[project_id], vars={}))
                        else:
                            session.flash = f'Ошибка при создании комплекта: {result.get("error", "Неизвестная ошибка")}'
                            show_complect_panel = True
        elif form_complect.errors:
            show_complect_panel = True
        if form_complect.element('input[type=submit]'):
            form_complect.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
        # ID статусов комплекта для кнопок
        complect_status_rop_id = 2
        complect_status_ispravlenie_id = 3
        complect_status_kp_soglasovano_id = 4  # КП согласовано
        complect_status_kp_otpravleno_id = 5    # КП отправлено
        complect_status_zakaz_id = 6            # Заказ
        # Если хоть у одного комплекта статус не «Черновик», кнопки КП и На согласование РОПу скрываем у всех
        has_non_chernovik = any(comp.complect_statuses and getattr(comp.complect_statuses, 'name', '') != 'Черновик' for comp in complects) if complects else False
        # Хлебные крошки (из modules, чтобы не конфликтовать с models)
        if customer:
            breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
                ('Главная', URL('default', 'index')),
                ('Клиенты', URL('customers', 'customers_list')),
                (customer.name, URL('customers', 'customer', args=[customer.id])),
                (project.name or project.project_number or 'Проект', None),
            ])
        else:
            breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
                ('Главная', URL('default', 'index')),
                (project.name or project.project_number or 'Проект', None),
            ])
        return dict(
            project=project,
            customer=customer,
            status=status,
            complects=complects,
            orders=orders,
            status_colors=status_colors,
            complect_status_colors=complect_status_colors,
            form_complect=form_complect,
            show_complect_panel=show_complect_panel,
            complect_status_rop_id=complect_status_rop_id,
            complect_status_ispravlenie_id=complect_status_ispravlenie_id,
            complect_status_kp_soglasovano_id=complect_status_kp_soglasovano_id,
            complect_status_kp_otpravleno_id=complect_status_kp_otpravleno_id,
            complect_status_zakaz_id=complect_status_zakaz_id,
            has_non_chernovik=has_non_chernovik,
            breadcrumbs=breadcrumbs,
        )
    except HTTP:
        # Пробрасываем HTTP исключения (редиректы) дальше
        raise
    except Exception as e:
        session.flash = f'Ошибка: {str(e)}'
        redirect(URL('default', 'index'))


def get_status_color(status_name):
    """
    Возвращает цвет для статуса проекта
    """
    colors = {
        'Лид': 'primary',
        'Заявка': 'info',
        'КП отправлено': 'warning',
        'КП согласовано': 'warning',
        'Заказ оформлен': 'success',
        'В производстве': 'danger',
        'Доставка': 'info',
        'Монтаж': 'primary',
        'Акт подписан': 'success',
        'Закрыт': 'secondary'
    }
    return colors.get(status_name, 'secondary')


def get_complect_status_color(status_name):
    """Возвращает цвет для статуса комплекта"""
    colors = {
        'Лид': 'primary',
        'Комплект': 'info',
        'Коммерческое предложение': 'warning',
        'Заказ': 'success',
        'Производство': 'danger'
    }
    return colors.get(status_name, 'secondary')
