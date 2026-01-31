# -*- coding: utf-8 -*-
"""
Контроллер для работы с клиентами
"""


def customer():
    """
    Карточка клиента
    """
    customer_id = request.args(0) or redirect(URL('default', 'index'))
    
    try:
        # Импортируем HTTP для обработки редиректов
        from gluon.http import HTTP
        import customers_service
        customer = customers_service.get_customer_by_id(db, customer_id)
        
        if not customer:
            session.flash = 'Клиент не найден'
            redirect(URL('default', 'index'))
        
        # Форма для добавления проекта (для sidebar)
        # Создаем форму без сохранения в БД (record=False)
        form_project = SQLFORM.factory(
            Field('name', 'string', length=200, requires=IS_NOT_EMPTY(), label='Название проекта'),
            Field('budget', 'decimal(10,2)', default=0, label='Бюджет проекта'),
            Field('start_date', 'date', label='Дата начала проекта'),
            Field('end_date', 'date', label='Дата окончания проекта'),
            Field('description', 'text', label='Описание проекта'),
            Field('notes', 'text', label='Примечания'),
            Field('sla_hours', 'integer', label='SLA - максимальное время в статусе (часы)'),
            submit_button='Добавить',
            _id='projectForm',
            _name='project_form',
            _action=URL('customers', 'customer', args=[customer_id]),
            _method='POST'
        )
        
        # Обработка формы добавления проекта
        show_project_panel = False
        if form_project.process(formname='project_form', keepvalues=False).accepted:
            # Получаем данные из формы безопасно
            project_name = str(form_project.vars.name) if form_project.vars.name else ''
            try:
                budget = float(form_project.vars.budget) if form_project.vars.budget else 0
            except:
                budget = 0
            start_date = form_project.vars.start_date if form_project.vars.start_date else None
            end_date = form_project.vars.end_date if form_project.vars.end_date else None
            description = str(form_project.vars.description) if form_project.vars.description else None
            notes = str(form_project.vars.notes) if form_project.vars.notes else None
            try:
                sla_hours = int(form_project.vars.sla_hours) if form_project.vars.sla_hours else None
            except:
                sla_hours = None
            
            # Генерируем номер проекта автоматически
            import projects_service
            project_number = projects_service.generate_project_number(db)
            
            # Создаем проект через сервисный слой с правильными параметрами
            result = projects_service.create_project(
                db=db,
                name=project_name,
                customer_id=customer_id,
                status_id=1,  # Автоматически устанавливаем статус = 1
                project_number=project_number,
                budget=budget,
                start_date=start_date,
                end_date=end_date,
                description=description,
                notes=notes,
                sla_hours=sla_hours
            )
            
            if result.get('success'):
                session.flash = 'Проект успешно добавлен'
                redirect(URL('customers', 'customer', args=[customer_id], vars={}))
            else:
                session.flash = f'Ошибка при создании проекта: {result.get("error", "Неизвестная ошибка")}'
                show_project_panel = True
        elif form_project.errors:
            show_project_panel = True
        
        # Настраиваем стили формы
        if form_project.element('input[type=submit]'):
            form_project.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
        
        # Получаем проекты клиента с информацией о статусах
        import project_statuses_service
        
        # Получаем проекты клиента с join к статусам
        projects = db(db.projects.customer_id == customer_id).select(
            db.projects.ALL,
            db.project_statuses.ALL,
            left=db.project_statuses.on(db.projects.status_id == db.project_statuses.id),
            orderby=~db.projects.created_on
        )
        
        # Получаем все статусы проектов для отображения
        all_statuses = project_statuses_service.get_all_statuses(db, is_active=True, order_by='sort_order')
        status_dict = {}
        status_colors = {}
        for status in all_statuses:
            status_dict[status.id] = status
            status_colors[status.id] = get_status_color(status.name)
        
        # Хлебные крошки: Главная → Клиенты → Клиент
        import breadcrumbs_helper
        breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
            ('Главная', URL('default', 'index')),
            ('Клиенты', URL('customers', 'customers_list')),
            (customer.name, None),
        ])
        return dict(
            customer=customer,
            projects=projects,
            status_dict=status_dict,
            status_colors=status_colors,
            form_project=form_project,
            show_project_panel=show_project_panel,
            breadcrumbs=breadcrumbs,
        )
    except HTTP:
        # Пробрасываем HTTP исключения (редиректы) дальше
        raise
    except Exception as e:
        session.flash = f'Ошибка: {str(e)}'
        redirect(URL('default', 'index'))


def customers_list():
    """
    Список всех клиентов
    """
    # Форма для добавления клиента (для sidebar)
    form_customer = SQLFORM(
        db.customers, 
        submit_button='Добавить', 
        _id='customerForm', 
        _name='customer_form',
        _action=URL('customers', 'customers_list'),
        _method='POST'
    )
    
    # Обработка формы добавления клиента
    if form_customer.process(formname='customer_form', keepvalues=False).accepted:
        customer_id = form_customer.vars.id
        session.flash = 'Клиент успешно добавлен'
        redirect(URL('customers', 'customer', args=[customer_id], vars={}))
    
    # Настраиваем стили формы
    if form_customer.element('input[type=submit]'):
        form_customer.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
    
    try:
        import customers_service
        
        # Параметры фильтрации и поиска
        search_term = request.vars.get('search', '')
        
        # Получаем всех клиентов
        if search_term:
            customers = customers_service.search_customers(db, search_term)
        else:
            customers = customers_service.get_all_customers(db, order_by='name')
        
        # Хлебные крошки: Главная → Клиенты
        import breadcrumbs_helper
        breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
            ('Главная', URL('default', 'index')),
            ('Клиенты', None),
        ])
        return dict(
            customers=customers,
            search_term=search_term,
            form_customer=form_customer,
            breadcrumbs=breadcrumbs,
        )
    except Exception as e:
        import breadcrumbs_helper
        breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
            ('Главная', URL('default', 'index')),
            ('Клиенты', None),
        ])
        return dict(
            customers=[],
            search_term='',
            form_customer=form_customer,
            breadcrumbs=breadcrumbs,
            error=str(e)
        )


def add_customer():
    """
    Добавление нового клиента (обработка формы)
    """
    import customers_service
    
    form = SQLFORM(db.customers, submit_button='Добавить')
    
    if form.process(formname='customer_form').accepted:
        # После успешного добавления перенаправляем на карточку клиента
        customer_id = form.vars.id
        session.flash = 'Клиент успешно добавлен'
        redirect(URL('customers', 'customer', args=[customer_id]))
    elif form.errors:
        session.flash = 'Ошибка при добавлении клиента: ' + ', '.join([str(v) for v in form.errors.values()])
        redirect(URL('default', 'index'))
    
    # Если форма не была отправлена, показываем форму
    return dict(form=form)


def get_status_color(status_name):
    """
    Возвращает цвет для статуса
    """
    colors = {
        'Лид': 'primary',
        'Заявка': 'info',
        'Коммерческое предложение': 'warning',
        'Заказ': 'success',
        'Производство': 'danger'
    }
    return colors.get(status_name, 'secondary')
