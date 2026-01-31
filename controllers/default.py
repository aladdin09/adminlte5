# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

import traceback
import sys

# Попытка импорта с обработкой ошибок
try:
    from dashboard_data import get_dashboard_data, get_status_color
except ImportError as e:
    # Если импорт не удался, попробуем альтернативные варианты
    try:
        import dashboard_data
        get_dashboard_data = dashboard_data.get_dashboard_data
        get_status_color = dashboard_data.get_status_color
    except Exception as e2:
        # Если и это не помогло, создадим заглушки
        def get_dashboard_data(db, request):
            return {'error': f'Ошибка импорта dashboard_data: {str(e)}, {str(e2)}'}
        def get_status_color(status_name):
            return 'secondary'


def index():
    """
    Дашборд + правая панель добавления клиента (главная страница).
    """
    try:
        show_customer_panel = False
        form_customer = SQLFORM(
            db.customers,
            submit_button='Добавить',
            _id='customerForm',
            _name='customer_form'
        )
        if form_customer.process(formname='customer_form').accepted:
            session.flash = 'Клиент успешно добавлен'
            redirect(URL('customers', 'customer', args=[form_customer.vars.id]))
        elif form_customer.errors:
            show_customer_panel = True
        if request.vars.get('open_customer_panel') == '1':
            show_customer_panel = True
        data = get_dashboard_data(db, request)
        form_customer.element('input[type=submit]')['_class'] = 'btn btn-primary btn-block'
        data['form_customer'] = form_customer
        data['show_customer_panel'] = show_customer_panel
        if 'error' not in data:
            data.setdefault('error', None)
        response.view = 'default/index.html'
        return data
    except Exception as e:
        # Детальная информация об ошибке для диагностики
        error_info = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc(),
            'sys_path': sys.path[:10],  # Первые 10 путей
            'request_vars': dict(request.vars),
            'request_args': request.args,
        }
        # Показываем детальную ошибку для диагностики
        # На боевом сервере это поможет понять проблему
        error_html = f"""
        <html><body>
        <h1>Ошибка в default/index</h1>
        <h2>Тип ошибки: {error_info['error_type']}</h2>
        <h3>Сообщение: {error_info['error_message']}</h3>
        <h3>Traceback:</h3>
        <pre>{error_info['traceback']}</pre>
        <h3>Sys path (первые 10):</h3>
        <pre>{error_info['sys_path']}</pre>
        </body></html>
        """
        raise HTTP(500, error_html)


def get_status_color_by_id(status_id):
    """
    Возвращает цвет для статуса по ID
    """
    try:
        status = db.complect_statuses(status_id)
        if status:
            return get_status_color(status.name)
    except:
        pass
    return 'secondary'



# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)




def test_reportlab():
    try:
        import reportlab
        return "ReportLab доступен"
    except Exception as e:
        return "ReportLab НЕ найден: " + str(e)
