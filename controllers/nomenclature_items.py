# -*- coding: utf-8 -*-
"""
Контроллер для работы с позициями номенклатуры
"""


def list():
    """
    Список всех позиций номенклатуры
    """
    import nomenclature_items_service
    
    search_term = request.vars.get('search', '')
    # Панель редактирования: при ?edit=id показываем форму в панели
    form_edit = None
    edit_item = None
    show_edit_panel = False
    edit_id = request.vars.get('edit')
    if edit_id:
        edit_item = nomenclature_items_service.get_nomenclature_item_by_id(db, edit_id)
        if edit_item:
            form_edit = SQLFORM(
                db.nomenclature_items,
                edit_id,
                submit_button='Сохранить',
                showid=False,
                _id='nomenclatureItemEditForm',
                _name='nomenclature_item_edit_form',
                _action=URL('nomenclature_items', 'list', vars=dict(edit=edit_id)),
                _method='POST'
            )
            if form_edit.process(formname='nomenclature_item_edit_form', keepvalues=False).accepted:
                session.flash = 'Позиция номенклатуры успешно обновлена'
                redirect(URL('nomenclature_items', 'list'))
            if form_edit.element('input[type=submit]'):
                form_edit.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
            show_edit_panel = True
    if search_term:
        items = nomenclature_items_service.search_nomenclature_items(db, search_term)
    else:
        items = nomenclature_items_service.get_all_nomenclature_items(db, order_by='created_on')
    import breadcrumbs_helper
    breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
        ('Главная', URL('default', 'index')),
        ('Номенклатура', None),
    ])
    return dict(
        items=items,
        search_term=search_term,
        breadcrumbs=breadcrumbs,
        form_edit=form_edit,
        edit_item=edit_item,
        show_edit_panel=show_edit_panel,
    )


def view():
    """
    Просмотр позиции номенклатуры
    """
    import nomenclature_items_service
    
    item_id = request.args(0)
    if not item_id:
        session.flash = 'Не указан ID позиции номенклатуры'
        redirect(URL('nomenclature_items', 'list'))
    
    item = nomenclature_items_service.get_nomenclature_item_by_id(db, item_id)
    if not item:
        session.flash = 'Позиция номенклатуры не найдена'
        redirect(URL('nomenclature_items', 'list'))
    # Форма редактирования в панели справа
    form_edit = SQLFORM(
        db.nomenclature_items,
        item_id,
        submit_button='Сохранить',
        showid=False,
        _id='nomenclatureItemEditFormView',
        _name='nomenclature_item_edit_form_view',
        _action=URL('nomenclature_items', 'view', args=[item_id]),
        _method='POST'
    )
    if form_edit.process(formname='nomenclature_item_edit_form_view', keepvalues=False).accepted:
        session.flash = 'Позиция номенклатуры успешно обновлена'
        redirect(URL('nomenclature_items', 'view', args=[item_id]))
    if form_edit.element('input[type=submit]'):
        form_edit.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
    import breadcrumbs_helper
    breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
        ('Главная', URL('default', 'index')),
        ('Номенклатура', URL('nomenclature_items', 'list')),
        (item.item_number or f'Позиция #{item.id}', None),
    ])
    return dict(item=item, form_edit=form_edit, breadcrumbs=breadcrumbs)


def create():
    """
    Создание новой позиции номенклатуры
    """
    import nomenclature_items_service
    
    # Генерируем номер по умолчанию
    default_number = nomenclature_items_service.generate_nomenclature_item_number(db)
    
    # Создаем форму
    form = SQLFORM(
        db.nomenclature_items,
        submit_button='Создать',
        _class='form-horizontal'
    )
    
    # Устанавливаем значение по умолчанию для номера
    if form.element('#nomenclature_items_item_number'):
        form.element('#nomenclature_items_item_number')['_value'] = default_number
    
    # Обработка формы
    if form.process().accepted:
        session.flash = 'Позиция номенклатуры успешно создана'
        redirect(URL('nomenclature_items', 'list'))
    elif form.errors:
        response.flash = 'Исправьте ошибки в форме'
    
    return dict(form=form, default_number=default_number)


def edit():
    """
    Редактирование позиции номенклатуры
    """
    import nomenclature_items_service
    
    item_id = request.args(0)
    if not item_id:
        session.flash = 'Не указан ID позиции номенклатуры'
        redirect(URL('nomenclature_items', 'list'))
    
    # Проверяем существование позиции
    item = nomenclature_items_service.get_nomenclature_item_by_id(db, item_id)
    if not item:
        session.flash = 'Позиция номенклатуры не найдена'
        redirect(URL('nomenclature_items', 'list'))
    
    # Создаем форму редактирования
    form = SQLFORM(
        db.nomenclature_items,
        item_id,
        submit_button='Сохранить',
        _class='form-horizontal',
        showid=False
    )
    
    # Обработка формы
    if form.process().accepted:
        session.flash = 'Позиция номенклатуры успешно обновлена'
        redirect(URL('nomenclature_items', 'list'))
    elif form.errors:
        response.flash = 'Исправьте ошибки в форме'
    
    return dict(form=form, item=item)


def delete():
    """
    Удаление позиции номенклатуры
    """
    import nomenclature_items_service
    
    item_id = request.args(0)
    if not item_id:
        session.flash = 'Не указан ID позиции номенклатуры'
        redirect(URL('nomenclature_items', 'list'))
    
    # Проверяем существование позиции
    item = nomenclature_items_service.get_nomenclature_item_by_id(db, item_id)
    if not item:
        session.flash = 'Позиция номенклатуры не найдена'
        redirect(URL('nomenclature_items', 'list'))
    
    # Удаляем позицию
    result = nomenclature_items_service.delete_nomenclature_item(db, item_id)
    
    if result.get('success'):
        session.flash = 'Позиция номенклатуры успешно удалена'
    else:
        session.flash = f'Ошибка при удалении позиции номенклатуры: {result.get("error", "Неизвестная ошибка")}'
    
    redirect(URL('nomenclature_items', 'list'))
