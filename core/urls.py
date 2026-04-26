from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/todo/add/', views.add_todo, name='add_todo'),
    path('api/todo/<int:todo_id>/toggle/', views.toggle_todo, name='toggle_todo'),
    path('api/todo/<int:todo_id>/delete/', views.delete_todo, name='delete_todo'),
]
