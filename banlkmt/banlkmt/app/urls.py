from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name="home"),
    path('search/', views.search, name="search"),
    path('success/', views.success, name="success"),
    path('detail/', views.detail, name="detail"),
    path('category/', views.category, name="category"),
    path('register/', views.register, name="register"),
    path('login/', views.loginForm, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_order/', views.updateOrder, name="update_order"),
]