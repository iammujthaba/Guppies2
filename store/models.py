from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250,unique=True)
    slug = models.SlugField(max_length=250,unique=True)
    image = models.ImageField(upload_to='category', blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categorys'

    # 2 - tis function is trigerd, and it call "product_by_category" url path name and pass catogory url as argument (go to urls.py)
    def get_url(self):
        return reverse('ecommerce_app:product_by_category',args=[self.slug])

    def __str__(self):
        return '{}'.format(self.name)
	
class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)

	def __str__(self):
		return self.name


class Product(models.Model):
	# name = models.CharField(max_length=200)
	# price = models.DecimalField(max_digits=7, decimal_places=2)
	digital = models.BooleanField(default=False,null=True, blank=True)
	# image = models.ImageField(null=True, blank=True)

	name = models.CharField(max_length=250,unique=True)
	slug = models.SlugField(max_length=250,unique=True)
	description = models.TextField(blank=True)
	old_price = models.DecimalField(max_digits=7,blank=True, decimal_places=2)
	new_price = models.DecimalField(max_digits=7,blank=False, decimal_places=2)
	category = models.ForeignKey(Category,on_delete=models.CASCADE)
	image_1 = models.ImageField(upload_to='product')
	image_2 = models.ImageField(upload_to='product',blank=True)
	image_3 = models.ImageField(upload_to='product',blank=True)
	video_url = models.URLField(max_length=200, blank=True)
	stock = models.IntegerField()
	available = models.BooleanField(default=True)
	new = models.BooleanField(default=True)
	created = models.DateTimeField(auto_now_add=True)
	update = models.DateField(auto_now=True)

	def get_url(self):
		return reverse('store_app:proDetail',args=[self.category.slug,self.slug])

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

    # def __str__(self):
    #     return '{}'.format(self.name)

	def __str__(self):
		return self.name

# if image is empty debug it with following code
	@property
	def imageURL(self):
		try:
			url = self.image_1.url
		except:
			url = ''
		return url

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)

	def __str__(self):
		return str(self.id)
	
	# cheking if product is digital or not to show shipping address
		# if eny one of the product have phesical to ship it will show address entering section by sending shipping is 'true'
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

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

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total = self.product.new_price * self.quantity
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	number = models.CharField(max_length=12, null=False, blank=False)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address