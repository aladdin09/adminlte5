# -*- coding: utf-8 -*-
"""
Общая логика данных для дашбордов (проекты, статусы, суммы).
Используется в default.index и в контроллерах dashboard_*.
"""


def get_status_color(status_name):
    """Цвет Bootstrap для статуса проекта."""
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


def get_dashboard_data(db, request):
    """
    Возвращает словарь данных для дашборда: проекты, статистика по статусам,
    суммы комплектов и т.д. Не включает форму клиента и show_customer_panel —
    их добавляет контроллер.
    """
    import project_statuses_service
    try:
        all_statuses = project_statuses_service.get_all_statuses(db, is_active=True, order_by='sort_order')
        dashboard_stats = []
        for status in all_statuses:
            try:
                projects_count = db(db.projects.status_id == status.id).count()
            except:
                projects_count = 0
            dashboard_stats.append({
                'name': status.name,
                'id': status.id,
                'count': projects_count,
                'color': get_status_color(status.name)
            })
        try:
            total_projects = db(db.projects.id > 0).count()
        except:
            total_projects = 0
        try:
            total_customers = db(db.customers.id > 0).count()
        except:
            total_customers = 0
        try:
            total_orders = db(db.orders.id > 0).count()
        except:
            total_orders = 0
        try:
            projects = db(db.projects.id > 0).select(
                db.projects.ALL,
                db.customers.ALL,
                db.project_statuses.ALL,
                left=[
                    db.customers.on(db.projects.customer_id == db.customers.id),
                    db.project_statuses.on(db.projects.status_id == db.project_statuses.id)
                ],
                orderby=~db.projects.created_on
            )
        except:
            projects = []
        try:
            all_customers = db(db.customers.id > 0).select(db.customers.id, db.customers.name, orderby=db.customers.name)
        except:
            all_customers = []
        all_statuses = project_statuses_service.get_all_statuses(db, is_active=True, order_by='sort_order')
        status_colors = {s.id: get_status_color(s.name) for s in all_statuses}
        complect_status_ids_for_sum = [2, 3, 4, 5, 6]
        project_complect_sums = {}
        try:
            rows = db((db.complects.project_id != None) & (db.complects.status_id.belongs(complect_status_ids_for_sum))).select(
                db.complects.project_id, db.complects.total_amount
            )
            for row in rows:
                pid = row.project_id
                project_complect_sums[pid] = project_complect_sums.get(pid, 0) + float(row.total_amount or 0)
        except Exception:
            pass
        dashboard_complect_total = sum(project_complect_sums.values())
        for stat in dashboard_stats:
            try:
                project_ids = [r.id for r in db(db.projects.status_id == stat['id']).select(db.projects.id)]
                stat['sum'] = sum(project_complect_sums.get(pid, 0) for pid in project_ids)
            except Exception:
                stat['sum'] = 0
        return dict(
            dashboard_stats=dashboard_stats,
            total_projects=total_projects,
            total_customers=total_customers,
            total_orders=total_orders,
            projects=projects,
            all_customers=all_customers,
            all_statuses=all_statuses,
            status_colors=status_colors,
            project_complect_sums=project_complect_sums,
            dashboard_complect_total=dashboard_complect_total,
            filter_customer=request.vars.get('filter_customer', ''),
            filter_status=request.vars.get('filter_status', ''),
            filter_name=request.vars.get('filter_name', ''),
            filter_project_number=request.vars.get('filter_project_number', ''),
        )
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        # Пытаемся получить хотя бы базовые данные
        try:
            import project_statuses_service
            all_statuses = project_statuses_service.get_all_statuses(db, is_active=True, order_by='sort_order')
            dashboard_stats = [{'name': s.name, 'id': s.id, 'count': 0, 'color': get_status_color(s.name), 'sum': 0} for s in all_statuses]
        except Exception as e2:
            dashboard_stats = []
            all_statuses = []
        return dict(
            dashboard_stats=dashboard_stats,
            total_projects=0,
            total_customers=0,
            total_orders=0,
            projects=[],
            all_customers=[],
            all_statuses=all_statuses if 'all_statuses' in locals() else [],
            status_colors={},
            project_complect_sums={},
            dashboard_complect_total=0,
            filter_customer='',
            filter_status='',
            filter_name='',
            filter_project_number='',
            error=str(e),
            error_traceback=error_traceback,
            error_type=type(e).__name__
        )
