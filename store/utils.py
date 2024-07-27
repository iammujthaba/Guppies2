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
	order = {'get_cart_total':0, 'get_cart_items':0}
	cartItems = order['get_cart_items']
	total_price_difference = 0

	for i in cart:
		#We use try block to prevent items in cart that may have been removed from causing error
		try:
			cartItems += cart[i]['quantity']

			product = Product.objects.get(id=i)
			total = (product.new_price * cart[i]['quantity'])

            # get total and quntity from cookies
			order['get_cart_total'] += total
			order['get_cart_items'] += cart[i]['quantity']

			price_difference = product.new_price - product.old_price
			total_price_difference += (cart[i]['quantity'])*price_difference

            # get and uppend into items, all information about product
			item = {
				'id':product.id,
				'product':{'id':product.id,'name':product.name, 
			   	'new_price':product.new_price, 'old_price':product.old_price,
				'imageURL':product.imageURL, 'get_url':product.get_url, 
				'active':product.active, 'stock':product.stock, 
				'price_difference':price_difference}, 

				'quantity':cart[i]['quantity'],
				'get_total':total,}
			items.append(item)

            # cheking if product is digital or not
			# if product.digital == False:
			# 	order['shipping'] = True
		except:
			pass
	return {'cartItems':cartItems ,'order':order, 'items':items, 'total_price_difference':total_price_difference}

def cartData(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
		total_price_difference = 0
	else:
		cookieData = cookieCart(request)
		cartItems = cookieData['cartItems']
		order = cookieData['order']
		items = cookieData['items']
		total_price_difference = cookieData['total_price_difference']
		print("............cartData.............")

	return {'cartItems':cartItems ,'order':order, 'items':items, 'total_price_difference':total_price_difference}

def cookieWishlist(request):
    try:
        wishlist = json.loads(request.COOKIES.get('wishlist', '{}'))
    except json.JSONDecodeError:
        wishlist = {}
    
    items = []
    wishlist_count = len(wishlist)

    for product_id in wishlist:
        try:
            product = Product.objects.get(id=product_id)
            item = {
                'id': product.id,
                'name': product.name,
                'image_url': product.imageURL,
                'price': product.new_price,
                'get_url': product.get_url,
            }
            items.append(item)
        except Product.DoesNotExist:
            pass

    return {'wishlist_items': items, 'wishlist_count': wishlist_count}

# from django.core.exceptions import ObjectDoesNotExist

# def cartData(request):
#     if request.user.is_authenticated:
#         try:
#             customer = request.user.customer
#         except ObjectDoesNotExist:
#             customer = Customer.objects.create(user=request.user)
        
#         order, created = Order.objects.get_or_create(customer=customer, complete=False)
#         items = order.orderitem_set.all()
#         cartItems = order.get_cart_items
#     else:
#         cookieData = cookieCart(request)
#         cartItems = cookieData['cartItems']
#         order = cookieData['order']
#         items = cookieData['items']
#     return {'cartItems': cartItems, 'order': order, 'items': items}


# unautherized user order prosessed here
# def guestOrder(request, data):
#     # save data in backend of an-authenticated user
#     print('User is not logged in')

#     # print('COOKIES:', request.COOKIES)
#     name = data['form']['name']
#     email = data['form']['email']

#     cookieData = cookieCart(request)
#     items = cookieData['items']

#     customer, created = Customer.objects.get_or_create(
#             email=email,
#             )
#     customer.name = name
#     customer.save()

#     order = Order.objects.create(
#         customer=customer,
#         complete=False,
#         )

#     for item in items:
#         product = Product.objects.get(id=item['id'])
#         orderItem = OrderItem.objects.create(
#             product=product,
#             order=order,
#             quantity=item['quantity'],
#         )
		
#     return customer, order
