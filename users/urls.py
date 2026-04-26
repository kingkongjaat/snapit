from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/users/login/'), name='logout'),
    path('search/', views.search_users, name='search'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    path('profile/<str:username>/status/', views.online_status, name='online_status'),
    path('profile/<str:username>/followers/', views.profile_followers, name='profile_followers'),
    path('profile/<str:username>/following/', views.profile_following, name='profile_following'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('ping/', views.ping_status, name='ping_status'),
]
