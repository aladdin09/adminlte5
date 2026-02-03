# -*- coding: utf-8 -*-
"""
Контроллер для работы с обязательными позициями в конкретной спецификации
"""


def list():
    """
    Список обязательных позиций в спецификациях. Добавление и редактирование через боковые панели.
    """
    edit_id = request.vars.get('edit')
    edit_item = None
    form_edit = None
    show_edit_panel = False

    if edit_id:
        try:
            edit_id = int(edit_id)
            edit_item = db.specification_required_items(edit_id)
        except (TypeError, ValueError):
            edit_item = None
        if edit_item:
            form_edit = SQLFORM(
                db.specification_required_items,
                edit_id,
                submit_button='Сохранить',
                showid=False,
                _id='specReqItemEditForm',
                _name='specification_required_item_edit_form',
                _action=URL('specification_required_items', 'list', vars=dict(edit=edit_id)),
                _method='POST'
            )
            if form_edit.process(formname='specification_required_item_edit_form', keepvalues=False).accepted:
                session.flash = 'Запись обновлена'
                redirect(URL('specification_required_items', 'list'))
            if form_edit.element('input[type=submit]'):
                form_edit.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
            show_edit_panel = True

    form_create = SQLFORM(
        db.specification_required_items,
        submit_button='Создать',
        _id='specReqItemCreateForm',
        _name='specification_required_item_create_form',
        _action=URL('specification_required_items', 'list'),
        _method='POST'
    )
    if form_create.process(formname='specification_required_item_create_form', keepvalues=False).accepted:
        session.flash = 'Запись создана'
        redirect(URL('specification_required_items', 'list'))
    if form_create.element('input[type=submit]'):
        form_create.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'

    rows = db(db.specification_required_items.id > 0).select(
        db.specification_required_items.ALL,
        db.specifications.ALL,
        db.parts.ALL,
        db.required_item_templates.ALL,
        left=[
            db.specifications.on(db.specification_required_items.spec_id == db.specifications.id),
            db.parts.on(db.specification_required_items.part_id == db.parts.id),
            db.required_item_templates.on(db.specification_required_items.template_id == db.required_item_templates.id),
        ],
        orderby=~db.specification_required_items.id
    )

    import breadcrumbs_helper
    breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
        ('Главная', URL('default', 'index')),
        ('Обязательные позиции в спецификации', None),
    ])
    return dict(
        rows=rows,
        breadcrumbs=breadcrumbs,
        form_create=form_create,
        form_edit=form_edit,
        show_edit_panel=show_edit_panel,
        edit_item=edit_item,
    )


def delete():
    rec_id = request.args(0)
    if not rec_id:
        session.flash = 'Не указан ID'
        redirect(URL('specification_required_items', 'list'))
    try:
        rec_id = int(rec_id)
    except (TypeError, ValueError):
        session.flash = 'Неверный ID'
        redirect(URL('specification_required_items', 'list'))
    row = db.specification_required_items(rec_id)
    if not row:
        session.flash = 'Запись не найдена'
        redirect(URL('specification_required_items', 'list'))
    db(db.specification_required_items.id == rec_id).delete()
    db.commit()
    session.flash = 'Запись удалена'
    redirect(URL('specification_required_items', 'list'))
