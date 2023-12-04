from django.urls import path
from . import views


urlpatterns = [
    # AUTH ROUTE
    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    
    # GENERAL ROUTE
    path('', views.home, name="home"),
    path('/profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('room/<str:id>/', views.room, name="room"),
    path('new-room/', views.createRoom, name="new-room"),
    path('update-room/<str:id>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:id>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:id>/', views.deleteMessage, name="delete-message"),
]