# -*- coding: utf-8 -*-
"""
Контроллер для работы с допустимыми материалами для обязательной позиции
"""


def list():
    """
    Список допустимых материалов. Добавление и редактирование через боковые панели.
    """
    edit_id = request.vars.get('edit')
    edit_item = None
    form_edit = None
    show_edit_panel = False

    if edit_id:
        try:
            edit_id = int(edit_id)
            edit_item = db.required_item_materials(edit_id)
        except (TypeError, ValueError):
            edit_item = None
        if edit_item:
            form_edit = SQLFORM(
                db.required_item_materials,
                edit_id,
                submit_button='Сохранить',
                showid=False,
                _id='requiredItemMaterialEditForm',
                _name='required_item_material_edit_form',
                _action=URL('required_item_materials', 'list', vars=dict(edit=edit_id)),
                _method='POST'
            )
            if form_edit.process(formname='required_item_material_edit_form', keepvalues=False).accepted:
                session.flash = 'Запись обновлена'
                redirect(URL('required_item_materials', 'list'))
            if form_edit.element('input[type=submit]'):
                form_edit.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
            show_edit_panel = True

    form_create = SQLFORM(
        db.required_item_materials,
        submit_button='Создать',
        _id='requiredItemMaterialCreateForm',
        _name='required_item_material_create_form',
        _action=URL('required_item_materials', 'list'),
        _method='POST'
    )
    if form_create.process(formname='required_item_material_create_form', keepvalues=False).accepted:
        session.flash = 'Запись создана'
        redirect(URL('required_item_materials', 'list'))
    if form_create.element('input[type=submit]'):
        form_create.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'

    rows = db(db.required_item_materials.id > 0).select(
        db.required_item_materials.ALL,
        db.required_item_templates.ALL,
        db.nomenclature_items.ALL,
        left=[
            db.required_item_templates.on(db.required_item_materials.required_item_template_id == db.required_item_templates.id),
            db.nomenclature_items.on(db.required_item_materials.nomenclature_id == db.nomenclature_items.id),
        ],
        orderby=db.required_item_materials.id
    )

    import breadcrumbs_helper
    breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
        ('Главная', URL('default', 'index')),
        ('Допустимые материалы для обязательной позиции', None),
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
        redirect(URL('required_item_materials', 'list'))
    try:
        rec_id = int(rec_id)
    except (TypeError, ValueError):
        session.flash = 'Неверный ID'
        redirect(URL('required_item_materials', 'list'))
    row = db.required_item_materials(rec_id)
    if not row:
        session.flash = 'Запись не найдена'
        redirect(URL('required_item_materials', 'list'))
    db(db.required_item_materials.id == rec_id).delete()
    db.commit()
    session.flash = 'Запись удалена'
    redirect(URL('required_item_materials', 'list'))
