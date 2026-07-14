from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('food/', views.food_log_view, name='food_log'),
    path('food/delete/<int:pk>/', views.delete_food_view, name='delete_food'),
    path('exercise/', views.exercise_log_view, name='exercise_log'),
    path('exercise/delete/<int:pk>/', views.delete_exercise_view, name='delete_exercise'),
    path('water/quick-add/', views.quick_add_water_view, name='quick_add_water'),
    path('weight/log/', views.weight_log_view, name='weight_log'),
    path('weight/delete/<int:pk>/', views.delete_weight_view, name='delete_weight'),
]
