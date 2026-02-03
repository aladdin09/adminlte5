# -*- coding: utf-8 -*-
"""
Контроллер для работы с частями дома (parts)
"""


def list():
    """
    Список частей дома. Добавление и редактирование через боковые панели.
    """
    edit_id = request.vars.get('edit')
    edit_item = None
    form_edit = None
    show_edit_panel = False

    # Панель редактирования: при ?edit=id показываем форму в панели
    if edit_id:
        try:
            edit_id = int(edit_id)
            edit_item = db.parts(edit_id)
        except (TypeError, ValueError):
            edit_item = None
        if edit_item:
            form_edit = SQLFORM(
                db.parts,
                edit_id,
                submit_button='Сохранить',
                showid=False,
                _id='partEditForm',
                _name='part_edit_form',
                _action=URL('parts', 'list', vars=dict(edit=edit_id)),
                _method='POST'
            )
            if form_edit.process(formname='part_edit_form', keepvalues=False).accepted:
                session.flash = 'Часть дома успешно обновлена'
                redirect(URL('parts', 'list'))
            if form_edit.element('input[type=submit]'):
                form_edit.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
            show_edit_panel = True

    # Форма добавления
    form_create = SQLFORM(
        db.parts,
        submit_button='Создать',
        _id='partCreateForm',
        _name='part_create_form',
        _action=URL('parts', 'list'),
        _method='POST'
    )
    if form_create.process(formname='part_create_form', keepvalues=False).accepted:
        session.flash = 'Часть дома успешно создана'
        redirect(URL('parts', 'list'))
    if form_create.element('input[type=submit]'):
        form_create.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'

    parts_list = db(db.parts).select(orderby=db.parts.name)

    import breadcrumbs_helper
    breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
        ('Главная', URL('default', 'index')),
        ('Части дома', None),
    ])
    return dict(
        parts_list=parts_list,
        breadcrumbs=breadcrumbs,
        form_create=form_create,
        form_edit=form_edit,
        show_edit_panel=show_edit_panel,
        edit_item=edit_item,
    )


def delete():
    """
    Удаление части дома
    """
    part_id = request.args(0)
    if not part_id:
        session.flash = 'Не указан ID части дома'
        redirect(URL('parts', 'list'))
    try:
        part_id = int(part_id)
    except (TypeError, ValueError):
        session.flash = 'Неверный ID'
        redirect(URL('parts', 'list'))
    row = db.parts(part_id)
    if not row:
        session.flash = 'Часть дома не найдена'
        redirect(URL('parts', 'list'))
    db(db.parts.id == part_id).delete()
    db.commit()
    session.flash = 'Часть дома удалена'
    redirect(URL('parts', 'list'))
