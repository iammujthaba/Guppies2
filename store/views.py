from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from .models import * 
from . utils import cartData, guestOrder

def store(request):

	data = cartData(request)
	cartItems = data['cartItems']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)

def cart(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

# order prossesing fuction deppending on user is authenticated or not
def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)

	else:
		# calling guestOrder function from util.py for un-authenticated user to prossess order
		customer, order = guestOrder(request, data)

	# cheking if user pyed amount and we requsted amount is same (cheking for any manupulation is happening)
	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
		order.save()
		success = True
		message = "Transaction completed"
	else:
		success = False
		message = "Something went wrong. Order not placed."

	# after peyment was succeed order.shipping will True, wich allow to save shipping address in database
	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		number=data['shipping']['number'],
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	# Empty the cart after payment for authenticated users
	if request.user.is_authenticated:
		order.orderitem_set.all().delete()

	return JsonResponse({'success': success, 'message': message}, safe=False)