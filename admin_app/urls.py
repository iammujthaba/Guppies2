from django.urls import path
from . import views

app_name = 'admin_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin_app/categories/', views.category_list, name='category_list'),
    path('admin_app/categories/create/', views.category_create, name='category_create'),
    path('admin_app/categories/update/<int:pk>/', views.category_update, name='category_update'),
    path('admin_app/categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    path('admin_app/products/', views.product_list, name='product_list'),
    path('admin_app/products/create/', views.product_create, name='product_create'),
    path('admin_app/products/update/<int:pk>/', views.product_update, name='product_update'),
    path('admin_app/products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('admin_app/orders/', views.order_list, name='order_list'),
    path('admin_app/orders/detail/<int:pk>/', views.order_detail, name='order_detail'),
]
