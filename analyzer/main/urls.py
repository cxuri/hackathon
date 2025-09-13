
from django.urls import path, include
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path("analyze/", views.analyze_images, name="analyze"),
]