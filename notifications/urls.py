from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('mark-read/', views.mark_all_read, name='mark_all_read'),
    path('unread/', views.unread_count, name='unread_count'),
    path('to/<int:notif_id>/', views.redirect_notification, name='redirect_notification'),
]
