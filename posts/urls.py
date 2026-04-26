from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('<int:post_id>/likers/', views.post_likers, name='post_likers'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('comment/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
]
