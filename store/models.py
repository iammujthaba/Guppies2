from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
# from django import forms

class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    image = models.ImageField(upload_to='category', blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categorys'

    def get_url(self):
        return reverse('store_app:product_by_category', args=[self.slug])

    def __str__(self):
        return '{}'.format(self.name)


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    # default_phone = models.CharField(max_length=15, null=True, blank=True)
    # default_address = models.CharField(max_length=200, null=True, blank=True)
    # default_city = models.CharField(max_length=200, null=True, blank=True)
    # default_state = models.CharField(max_length=200, null=True, blank=True)
    # default_zipcode = models.CharField(max_length=10, null=True, blank=True)
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    old_price = models.DecimalField(max_digits=7, blank=True, null=True, decimal_places=2)
    new_price = models.DecimalField(max_digits=7, blank=False, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image_1 = models.ImageField(upload_to='product')
    image_2 = models.ImageField(upload_to='product', blank=True)
    image_3 = models.ImageField(upload_to='product', blank=True)
    video_url = models.URLField(max_length=200, blank=True)
    stock = models.IntegerField()
    active = models.BooleanField(default=True)
    new = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateField(auto_now=True)

    def get_url(self):
        return reverse('store_app:proDetail', args=[self.category.slug, self.slug])

    def get_discounted_price(self):
        if self.old_price and self.new_price:
            diff = self.old_price - self.new_price
            discount_percentage = ((diff) / self.old_price) * 100
            percentage = int(round(discount_percentage))
            return dict(percentage=percentage, diff=diff)
        return None

    class Meta:
        ordering = ('name',)
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image_1.url
        except:
            url = ''
        return url


class Order(models.Model):
    STATUS_CHOICES = [
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')
    processing_time = models.DateTimeField(null=True, blank=True)
    shipped_time = models.DateTimeField(null=True, blank=True)
    delivered_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def save(self, *args, **kwargs):
        if self.status == 'Processing' and not self.processing_time:
            self.processing_time = timezone.now()
        elif self.status == 'Shipped' and not self.shipped_time:
            self.shipped_time = timezone.now()
        elif self.status == 'Delivered' and not self.delivered_time:
            self.delivered_time = timezone.now()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    price_at_purchase = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    @property
    def get_total(self):
        if self.price_at_purchase is None:
            self.price_at_purchase = self.product.new_price
        return self.price_at_purchase * self.quantity

    def save(self, *args, **kwargs):
        if not self.price_at_purchase:
            self.price_at_purchase = self.product.new_price
        super().save(*args, **kwargs)


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    number = models.CharField(max_length=12, null=False, blank=False)
    whatsapp = models.CharField(max_length=12, null=False, blank=False)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class PurchaseHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price_at_purchase = models.DecimalField(max_digits=7, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.product.name}"

# class ShippingInfoForm(forms.ModelForm):
#     class Meta:
#         model = Customer
#         fields = ['default_phone', 'default_address', 'default_city', 'default_state', 'default_zipcode']
#         widgets = {
#             'default_phone': forms.TextInput(attrs={'class': 'form-control'}),
#             'default_address': forms.TextInput(attrs={'class': 'form-control'}),
#             'default_city': forms.TextInput(attrs={'class': 'form-control'}),
#             'default_state': forms.TextInput(attrs={'class': 'form-control'}),
#             'default_zipcode': forms.TextInput(attrs={'class': 'form-control'}),
#         }