from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.http import JsonResponse
import json
import datetime

from .models import * 
from . utils import cartData, guestOrder


def allProdCat(request, c_slug = None):
    c_page = None
    offer = None
    products_list = None
    # 4 - tis "if" condition work when "product_by_category" path is call "allProdCat" function [its hpappaning]
    # and "c_slug" change its valure from "None" to catogory url (go to "get_object_or_404")
    if c_slug != None:
        # 5 - tis "get_object_or_404" function return catogory url corresponding Catogory method name (go to 6)
        c_page = get_object_or_404(Category, slug = c_slug)
        # 6 - tis line of code take all product listed under, user cliked catogory (done.)
        products_list = Product.objects.all().filter(category = c_page, available = True, stock__gt=0)
    else:
        products_list = Product.objects.all().filter(available = True, stock__gt=0)


    paginator = Paginator(products_list,6)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        products = paginator.page(page)
    except (InvalidPage,EmptyPage):
        products = paginator.page(paginator.num_pages)
        
    offer = Product.objects.filter(old_price__gt=0)

    return render(request,'store/category.html',{'category':c_page, 'products':products, 'offer':offer})


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

	if action == 'remove-all':
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
	total = data['form']['total']
	order.transaction_id = transaction_id
	print(order.transaction_id)

	if total == str(order.get_cart_total):
		order.complete = True
		order.save()
		success = True
		message = "Transaction completed, \nYou'r Order placed Successfully..."

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

		# to set cart as Empty (the cart will empty after payment for authenticated users)
		# if request.user.is_authenticated:
		# 		# order.orderitem_set.all().delete()
		# 	# order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
		# 	# order['get_cart_items']

	else:
		success = False
		message = "Something went wrong! \nOrder not placed, For More Contact Us"

	
	return JsonResponse({'success': success, 'message': message}, safe=False)


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


def proDetail(request, c_slug, product_slug):
    try:
        product = Product.objects.get(category__slug = c_slug, slug = product_slug)
    except Exception as e:
        raise e
    
    if c_slug:
        c_page = get_object_or_404(Category, slug = c_slug)
        products_list = Product.objects.all().filter(category = c_page, available = True)

    paginator = Paginator(products_list,5)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        products = paginator.page(page)
    except (InvalidPage,EmptyPage):
        products = paginator.page(paginator.num_pages)


    return render(request, 'store/product.html',{'product':product,'products':products})



def allProductListing(request):
    products_list = Product.objects.all().filter(available = True)

    paginator = Paginator(products_list,14)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        products = paginator.page(page)
    except (InvalidPage,EmptyPage):
        products = paginator.page(paginator.num_pages)
        
    return render(request,'store/shop.html',{'products':products})

def offerProductListing(request):
    products_list = Product.objects.filter(old_price__gt=0)

    paginator = Paginator(products_list,14)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        products = paginator.page(page)
    except (InvalidPage,EmptyPage):
        products = paginator.page(paginator.num_pages)
        
    return render(request,'store/shop.html',{'products':products})


