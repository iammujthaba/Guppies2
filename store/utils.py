import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except:
        cart = {}
    
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = order['get_cart_items']
    total_price_difference = 0
    
    for i in cart:
        try:
            product = Product.objects.get(id=i)
            quantity = cart[i]['quantity']
            total = (product.new_price * quantity)
            order['get_cart_total'] += total
            order['get_cart_items'] += quantity
            
            # Ensure old_price is a number, defaulting to new_price if None or 0
            old_price = product.old_price if product.old_price and product.old_price > product.new_price else product.new_price
            
            # Calculate price difference only if there's a actual discount
            price_difference = (old_price - product.new_price) * quantity if old_price > product.new_price else 0
            total_price_difference += price_difference
            
            item = {
                'id': product.id,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'new_price': product.new_price,
                    'old_price': old_price,
                    'imageURL': product.imageURL,
                    'get_url': product.get_url,
                    'active': product.active,
                    'stock': product.stock,
                    'price_difference': price_difference / quantity,  # Store per-item price difference
                    'get_discounted_price': product.get_discounted_price(),
                },
                'quantity': quantity,
                'get_total': total,
            }
            items.append(item)
        except Exception as e:
            print(f"Error processing product {i}: {str(e)}")
            pass
    
    return {'cartItems': cartItems, 'order': order, 'items': items, 'total_price_difference': total_price_difference}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        total_price_difference = sum((item.product.old_price - item.product.new_price if item.product.old_price else 0) * item.quantity for item in items)
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
        total_price_difference = cookieData['total_price_difference']
    
    return {'cartItems': cartItems, 'order': order, 'items': items, 'total_price_difference': total_price_difference}

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
                'stock': product.stock,
                'image_url': product.imageURL,
                'new_price': product.new_price,
                'old_price': product.old_price,
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
