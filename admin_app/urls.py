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
    # path('admin_app/products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('admin_app/orders/pending/<int:pk>/', views.order_view, name='order_view'),
    path('admin_app/orders/processing/', views.processing_orders, name='processing_orders'),
    path('admin_app/orders/confirmed/', views.confirmed_orders, name='confirmed_orders'),
    path('admin_app/orders/shipped/', views.shipped_orders, name='shipped_orders'),
    path('admin_app/orders/completed/', views.completed_orders, name='completed_orders'),
    path('admin_app/users/', views.users_list, name='users_list'),
]
