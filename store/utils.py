import json
from .models import *

def cookieCart(request):

	# if user is not authenticated, load user data from cookies
	try:
		cart = json.loads(request.COOKIES['cart'])
	except:
		cart = {}
		print('CART:', cart)

    #Create empty cart for now for non-logged in user
	items = []
	order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
	cartItems = order['get_cart_items']

	for i in cart:
		#We use try block to prevent items in cart that may have been removed from causing error
		try:
			cartItems += cart[i]['quantity']

			product = Product.objects.get(id=i)
			total = (product.price * cart[i]['quantity'])

            # get total and quntity from cookies
			order['get_cart_total'] += total
			order['get_cart_items'] += cart[i]['quantity']

            # get and uppend into items, all information about product
			item = {
				'id':product.id,
				'product':{'id':product.id,'name':product.name, 'price':product.price, 
				'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
				'digital':product.digital,'get_total':total,
				}
			items.append(item)

            # cheking if product is digital or not
			if product.digital == False:
				order['shipping'] = True
		except:
			pass
			
	return {'cartItems':cartItems ,'order':order, 'items':items}