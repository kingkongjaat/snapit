from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('with/<str:username>/', views.conversation, name='conversation'),
    path('send/<int:conv_id>/', views.send_message, name='send_message'),
    path('unread/', views.unread_message_count, name='unread_count'),
]
