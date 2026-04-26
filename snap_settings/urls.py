from django.urls import path
from . import views
from . import admin_views

app_name = 'snap_settings'

urlpatterns = [
    path('', views.settings_page, name='settings'),
    path('report/', views.submit_report, name='report'),
    path('feedback/', views.submit_feedback, name='feedback'),
    
    # Admin Portal
    path('admin-portal/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-portal/reports/', admin_views.admin_reports, name='admin_reports'),
    path('admin-portal/feedbacks/', admin_views.admin_feedbacks, name='admin_feedbacks'),
    path('admin-portal/reports/<int:report_id>/resolve/', admin_views.admin_resolve_report, name='admin_resolve_report'),
    path('admin-portal/users/<int:user_id>/warn/', admin_views.admin_warn_user, name='admin_warn_user'),
    path('admin-portal/users/<int:user_id>/ban/', admin_views.admin_ban_user, name='admin_ban_user'),
]

