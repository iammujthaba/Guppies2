from django.contrib import admin

from .models import *

admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)

# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['name', 'slug']
#     prepopulated_fields = {'slug':('name',)}
# admin.site.register(Category,CategoryAdmin)

# class ProductAdmin(admin.ModelAdmin):
#     list_display = ['name', 'old_price','new_price', 'stock', 'available','new', 'category','update']
#     list_editable = ['new_price','old_price','new', 'stock', 'available']
#     prepopulated_fields = {'slug':('name',)}
#     list_per_page = 20
# admin.site.register(Product,ProductAdmin)