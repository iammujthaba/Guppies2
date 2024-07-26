from django.urls import path

from . import views

app_name = 'store_app'
urlpatterns = [
	path('', views.allProdCat, name="allProdCat"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    
	path('<slug:c_slug>/slug',views.allProdCat,name='product_by_category'), #called form models.py
    path('<slug:c_slug>/<slug:product_slug>/',views.proDetail,name='proDetail'), #called form models.py
    path('shop/',views.allProductListing,name='allProductListing'),
    path('offer/',views.offerProductListing,name='offerProductListing'),
    path('category/',views.Category_list,name='category_list'),
    path('account/',views.account_info,name='account_info'),
    path('orders/',views.orders,name='orders'),

    path('about/',views.about,name='about'),
    path('gallery/',views.gallery,name='gallery'),
    path('contact/',views.contact,name='contact'),
    path('Questions/',views.faq,name='faq'),
    path('devolopper/',views.devolopper,name='devolopper'),

    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
]