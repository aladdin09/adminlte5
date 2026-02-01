# -*- coding: utf-8 -*-
"""
Контроллер для работы со статусами комплектов
"""


def list():
    """Список всех статусов комплектов"""
    try:
        # Откатываем любые незавершенные транзакции перед началом
        try:
            db.rollback()
        except:
            pass
        
        import complect_statuses_service
        import importlib
        importlib.reload(complect_statuses_service)
        # Форма для добавления статуса (в панели справа)
        form_status = SQLFORM(
            db.complect_statuses,
            submit_button='Добавить',
            _id='complectStatusForm',
            _name='complect_status_form',
            _action=URL('complect_statuses', 'list'),
            _method='POST'
        )
        if form_status.process(formname='complect_status_form', keepvalues=False).accepted:
            session.flash = 'Статус комплекта успешно создан'
            redirect(URL('complect_statuses', 'list'))
        if form_status.element('input[type=submit]'):
            form_status.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
        # Панель редактирования: при ?edit=id показываем форму редактирования в панели
        edit_status = None
        form_edit = None
        show_edit_panel = False
        edit_id = request.vars.get('edit')
        if edit_id:
            try:
                edit_status = complect_statuses_service.get_status_by_id(db, edit_id)
            except Exception as e:
                # Откатываем транзакцию при ошибке
                try:
                    db.rollback()
                except:
                    pass
                edit_status = None
            if edit_status:
                form_edit = SQLFORM(
                    db.complect_statuses,
                    edit_id,
                    submit_button='Сохранить',
                    showid=False,
                    _id='complectStatusEditForm',
                    _name='complect_status_edit_form',
                    _action=URL('complect_statuses', 'list', vars=dict(edit=edit_id)),
                    _method='POST'
                )
                if form_edit.process(formname='complect_status_edit_form', keepvalues=False).accepted:
                    session.flash = 'Статус комплекта успешно обновлён'
                    redirect(URL('complect_statuses', 'list'))
                if form_edit.element('input[type=submit]'):
                    form_edit.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
                show_edit_panel = True
        try:
            statuses = complect_statuses_service.get_all_statuses(db, order_by='sort_order')
        except Exception as e:
            # Откатываем транзакцию при ошибке
            try:
                db.rollback()
            except:
                pass
            # Пробуем еще раз после rollback
            try:
                statuses = complect_statuses_service.get_all_statuses(db, order_by='sort_order')
            except Exception as e2:
                statuses = []
                session.flash = f'Ошибка загрузки статусов: {str(e2)}'
        import breadcrumbs_helper
        breadcrumbs = breadcrumbs_helper.make_breadcrumbs([
            ('Главная', URL('default', 'index')),
            ('Статус комплекта', None),
        ])
        return dict(
            statuses=statuses,
            breadcrumbs=breadcrumbs,
            form_status=form_status,
            form_edit=form_edit,
            edit_status=edit_status,
            show_edit_panel=show_edit_panel,
        )
    except Exception as e:
        # Откатываем транзакцию при критической ошибке
        try:
            db.rollback()
        except:
            pass
        session.flash = f'Ошибка: {str(e)}'
        redirect(URL('default', 'index'))


def create():
    """Создание нового статуса комплекта"""
    try:
        # Откатываем любые незавершенные транзакции
        try:
            db.rollback()
        except:
            pass
        
        import complect_statuses_service
        import importlib
        importlib.reload(complect_statuses_service)
        form = SQLFORM(db.complect_statuses, submit_button='Создать', _class='form-horizontal')
        if form.process().accepted:
            session.flash = 'Статус комплекта успешно создан'
            redirect(URL('complect_statuses', 'list'))
        elif form.errors:
            response.flash = 'Исправьте ошибки в форме'
        return dict(form=form)
    except Exception as e:
        try:
            db.rollback()
        except:
            pass
        session.flash = f'Ошибка: {str(e)}'
        redirect(URL('complect_statuses', 'list'))


def edit():
    """Редактирование статуса комплекта"""
    try:
        # Откатываем любые незавершенные транзакции
        try:
            db.rollback()
        except:
            pass
        
        import complect_statuses_service
        import importlib
        importlib.reload(complect_statuses_service)
        status_id = request.args(0)
        if not status_id:
            session.flash = 'Не указан ID статуса'
            redirect(URL('complect_statuses', 'list'))
        try:
            status = complect_statuses_service.get_status_by_id(db, status_id)
        except Exception as e:
            try:
                db.rollback()
            except:
                pass
            status = None
        if not status:
            session.flash = 'Статус не найден'
            redirect(URL('complect_statuses', 'list'))
        form = SQLFORM(db.complect_statuses, status_id, submit_button='Сохранить', _class='form-horizontal', showid=False)
        if form.process().accepted:
            session.flash = 'Статус комплекта успешно обновлен'
            redirect(URL('complect_statuses', 'list'))
        elif form.errors:
            response.flash = 'Исправьте ошибки в форме'
        return dict(form=form, status=status)
    except Exception as e:
        try:
            db.rollback()
        except:
            pass
        session.flash = f'Ошибка: {str(e)}'
        redirect(URL('complect_statuses', 'list'))


def delete():
    """Удаление статуса комплекта"""
    try:
        # Откатываем любые незавершенные транзакции
        try:
            db.rollback()
        except:
            pass
        
        import complect_statuses_service
        import importlib
        importlib.reload(complect_statuses_service)
        status_id = request.args(0)
        if not status_id:
            session.flash = 'Не указан ID статуса'
            redirect(URL('complect_statuses', 'list'))
        try:
            status = complect_statuses_service.get_status_by_id(db, status_id)
        except Exception as e:
            try:
                db.rollback()
            except:
                pass
            status = None
        if not status:
            session.flash = 'Статус не найден'
            redirect(URL('complect_statuses', 'list'))
        result = complect_statuses_service.delete_status(db, status_id)
        if result.get('success'):
            session.flash = 'Статус комплекта успешно удален'
        else:
            session.flash = f'Ошибка при удалении статуса: {result.get("error", "Неизвестная ошибка")}'
        redirect(URL('complect_statuses', 'list'))
    except Exception as e:
        try:
            db.rollback()
        except:
            pass
        session.flash = f'Ошибка: {str(e)}'
        redirect(URL('complect_statuses', 'list'))
