from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cartData, cookieWishlist
from django.contrib.auth.decorators import login_required
import logging
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def allProdCat(request, c_slug=None):
    c_page = None
    offer = None
    products_list = None
    categories = Category.objects.all().order_by('priority', 'name')  # Get all categories
    
    if c_slug is not None:
        c_page = get_object_or_404(Category, slug=c_slug)
        products_list = Product.objects.filter(category=c_page, active=True, stock__gt=0)
    else:
        products_list = Product.objects.filter(active=True, stock__gt=0)
    
    offer_list = Product.objects.filter(active=True, old_price__gt=0, stock__gt=0)
    
    paginator1 = Paginator(products_list, 6)
    paginator2 = Paginator(offer_list, 6)
    
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    
    try:
        products = paginator1.page(page)
        offer = paginator2.page(page)
    except (InvalidPage, EmptyPage):
        products = paginator1.page(paginator1.num_pages)
        offer = paginator2.page(paginator2.num_pages)
    
    message_list = []
    for message in messages.get_messages(request):
        message_list.append({
            'message': message.message,
            'tags': message.tags
        })
    
    return render(request, 'store/category.html', {
        'category': c_page,
        'products': products,
        'offer': offer,
        'messages': message_list,
        'categories': categories,  # Pass all categories to the template
    })

from decimal import Decimal

def calculate_shipping(state, items):
    try:
        rate = ShippingRate.objects.get(state=state)
        base_rate = rate.base_rate
        additional_rate = rate.additional_item_rate
    except ShippingRate.DoesNotExist:
        # Default rates for other states
        base_rate = Decimal('180.00')
        additional_rate = Decimal('40.00')

    # Count total quantity of items
    total_quantity = sum(item.quantity for item in items)

    # Calculate additional charge based on total quantity
    additional_charge = additional_rate * (total_quantity - 1) if total_quantity > 1 else Decimal('0.00')

    total_shipping = base_rate + additional_charge
    return total_shipping


@csrf_exempt
def calculate_shipping_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        state = data.get('state')
        items = data.get('items')
        
        # Convert items to the format expected by calculate_shipping
        formatted_items = [type('obj', (object,), {'quantity': item['quantity']}) for item in items]
        
        shipping_charge = calculate_shipping(state, formatted_items)
        
        return JsonResponse({'shipping_charge': float(shipping_charge)})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    total_price_difference = data['total_price_difference']

    # Get all states for the dropdown
    all_states = ShippingRate.objects.values_list('state', flat=True)

    # Get the selected state or use the saved state for returning customers
    selected_state = request.GET.get('state')
    if not selected_state and request.user.is_authenticated:
        last_shipping = ShippingAddress.objects.filter(customer=request.user.customer).order_by('-date_added').first()
        if last_shipping:
            selected_state = last_shipping.state

    # Calculate shipping
    shipping_charge = calculate_shipping(selected_state, items) if selected_state else Decimal('0.00')

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'total_price_difference': total_price_difference,
        'all_states': all_states,
        'selected_state': selected_state,
        'shipping_charge': shipping_charge,
    }
    return render(request, 'store/Cart.html', context)

# def checkout(request):
#     if request.user.is_authenticated:
#         data = cartData(request)
#         cartItems = data['cartItems']
#         order = data['order']
#         items = data['items']

#         customer = request.user.customer
#         last_shipping = ShippingAddress.objects.filter(customer=customer).order_by('-date_added').first()

#         context = {
#             'items': items,
#             'order': order,
#             'cartItems': cartItems,
#             'last_shipping': last_shipping,
#         }
#         return render(request, 'store/Checkout.html', context)
#     else:
#         return redirect('store_app:account_info')



def checkout(request):
    if request.user.is_authenticated:
        data = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']
        customer = request.user.customer
        last_shipping = ShippingAddress.objects.filter(customer=customer).order_by('-date_added').first()

        if request.method == 'POST':
            # Process the form data
            shipping_info = {
                'number': request.POST.get('number'),
                'whatsapp': request.POST.get('whatsapp'),
                'address': request.POST.get('address'),
                'city': request.POST.get('city'),
                'state': request.POST.get('state'),
                'zipcode': request.POST.get('zipcode'),
            }
            # Store shipping info in session
            request.session['shipping_info'] = shipping_info
            return redirect('store_app:payment')  # Redirect to the new payment page


        # Get the last shipping information

        # customer = request.user.customer
        # last_shipping = ShippingAddress.objects.filter(customer=customer).order_by('-date_added').first()

        frequent_customer_areas = ["Kerala", "Karnataka", "Tamil Nadu"]
        other_states = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
                "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", 
                "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", 
                "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", 
                "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

        context = {
            'items': items,
            'order': order,
            'frequent_customer_areas': frequent_customer_areas,
            'other_states': other_states,
            'cartItems': cartItems,
            'last_shipping': last_shipping,
        }
        return render(request, 'store/Checkout.html', context)
    else:
        return redirect('store_app:account_info')

def payment(request):
    if request.user.is_authenticated:
        data = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']

        # Retrieve shipping info from session
        shipping_info = request.session.get('shipping_info', {})

        # Calculate shipping charge
        shipping_charge = calculate_shipping(shipping_info.get('state'), items)

        context = {
            'items': items,
            'order': order,
            'cartItems': cartItems,
            'shipping_info': shipping_info,
            'shipping_charge': shipping_charge,
        }
        return render(request, 'store/payment.html', context)
    else:
        return redirect('store_app:account_info')


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer if request.user.is_authenticated else None
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    added = True
    message = ""

    if action == 'add':
        if orderItem.quantity + 1 <= product.stock:
            orderItem.quantity += 1
            orderItem.save()
        else:
            added = False
            message = "There is no more stock available. If you want more, please contact us."
    elif action == 'remove':
        orderItem.quantity -= 1
        if orderItem.quantity <= 0:
            orderItem.delete()
        else:
            orderItem.save()
    elif action == 'remove-all':
        orderItem.delete()

    cart_total = order.get_cart_total
    cart_items = order.get_cart_items
    total_price_difference = sum((item.product.old_price - item.product.new_price if item.product.old_price else 0) * item.quantity for item in order.orderitem_set.all())

    return JsonResponse({
        'added': added,
        'message': message,
        'cartItems': cart_items,
        'cartTotal': cart_total,
        'totalPriceDifference': total_price_difference,
        'itemQuantity': orderItem.quantity if orderItem.id else 0,
        'itemTotal': orderItem.get_total if orderItem.id else 0,
    }, safe=False)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def processOrder(request):
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = Decimal(data['shipping']['total'])

        # Calculate shipping
        items = order.orderitem_set.all()
        shipping_state = data['shipping']['state']
        total_shipping = calculate_shipping(shipping_state, items)

        if total == Decimal(order.get_cart_total) + total_shipping:
            order.complete = True
            order.transaction_id = data['shipping']['razorpay_payment_id']
            order.save()

            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                number=data['shipping']['number'],
                whatsapp=data['shipping']['whatsapp'],
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

            # Process order items
            for item in order.orderitem_set.all():
                product = item.product
                product.stock -= item.quantity
                product.save()

                PurchaseHistory.objects.create(
                    customer=customer,
                    product=product,
                    price_at_purchase=item.price_at_purchase
                )

            # Clear the cart
            if 'cart' in request.session:
                del request.session['cart']
            request.session.modified = True

            return JsonResponse({'success': True, 'message': 'Order placed successfully!'})
        else:
            return JsonResponse({'success': False, 'message': 'Total price mismatch.'})
    else:
        return JsonResponse({'success': False, 'message': 'User not authenticated.'})


def proDetail(request, c_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=c_slug, slug=product_slug)

        in_wishlist = is_product_in_wishlist(request, product)

        if request.user.is_authenticated:
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        else:
            cookie_data = cookieWishlist(request)
            wishlist_count = cookie_data['wishlist_count']

    except Product.DoesNotExist:
        logger.error(f"Product not found: category_slug={c_slug}, product_slug={product_slug}")
        return render(request, 'store/error.html')

    if c_slug:
        c_page = get_object_or_404(Category, slug=c_slug)
        products_list = Product.objects.filter(category=c_page, active=True)
        paginator = Paginator(products_list, 5)
        try:
            page = int(request.GET.get('page', '1'))
        except (ValueError, TypeError):
            page = 1
        try:
            products = paginator.page(page)
        except (InvalidPage, EmptyPage):
            products = paginator.page(paginator.num_pages)

        return render(request, 'store/product.html', {
            'product': product,
            'products': products,
            'in_wishlist': in_wishlist,
            'wishlist_count': wishlist_count
        })
    else:
        return render(request, 'store/product.html', {
            'product': product,
            'in_wishlist': in_wishlist,
            'wishlist_count': wishlist_count
        })


def allProductListing(request):
    products_list = Product.objects.filter(active=True)
    categories = Category.objects.all().order_by('priority', 'name')  # Get all categories
    
    paginator = Paginator(products_list, 14)
    
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    
    try:
        products = paginator.page(page)
    except (InvalidPage, EmptyPage):
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'store/shop.html', {
        'products': products,
        'categories': categories,  # Pass all categories to the template
    })

def offerProductListing(request):
    products_list = Product.objects.filter(old_price__gt=0, active=True)
    categories = Category.objects.all().order_by('priority', 'name')  # Get all categories
    
    paginator = Paginator(products_list, 14)
    
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    
    try:
        products = paginator.page(page)
    except (InvalidPage, EmptyPage):
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'store/shop.html', {
        'products': products,
        'page': 'offer',
        'categories': categories,  # Pass all categories to the template
    })

def Category_list(request):
    categorys_list = Category.objects.all().order_by('priority', 'name')
    return render(request, 'store/category_listing.html', {'categorys_list': categorys_list})

# def orders(request):
#     if not request.user.is_authenticated:
#         return redirect('auth_app:login')

#     customer = request.user.customer
#     orders = Order.objects.filter(customer=customer, complete=True)

#     processing_orders = orders.filter(status='Processing')
#     confirmed_orders = orders.filter(status='Confirmed')
#     shipped_orders = orders.filter(status='Shipped')
#     delivered_orders = orders.filter(status='Delivered')

#     context = {
#         'user': request.user,
#         'processing_orders': processing_orders,
#         'confirmed_orders': confirmed_orders,
#         'shipped_orders': shipped_orders,
#         'delivered_orders': delivered_orders,
#     }

#     return render(request, 'store/orders.html', context)


from django.db.models import Sum

def myorders(request):
    if not request.user.is_authenticated:
        return redirect('auth_app:login')

    customer = request.user.customer

    if request.path == '/delivered/':
        orders = Order.objects.filter(customer=customer, complete=True, status='Delivered').order_by('-date_ordered')
    else:
        orders = Order.objects.filter(customer=customer, complete=True).exclude(status='Delivered').order_by('-date_ordered')

    orders_with_details = []
    for order in orders:
        total_quantity = OrderItem.objects.filter(order=order).aggregate(Sum('quantity'))['quantity__sum']
        orders_with_details.append({
            'order': order,
            'total_quantity': total_quantity or 0,
            'total_amount': order.get_cart_total,
            'date_ordered': order.date_ordered,
            'status': order.status,
        })

    context = {
        'user': request.user,
        'orders_with_details': orders_with_details,
    }
    return render(request, 'store/myorder.html', context)

# def track_order(request, order_id):
#     if not request.user.is_authenticated:
#         return redirect('auth_app:login')

#     order = Order.objects.get(id=order_id, customer=request.user.customer)
#     order_items = OrderItem.objects.filter(order=order)

#     context = {
#         'order': order,
#         'order_items': order_items,
#     }
#     return render(request, 'store/track_order.html', context)


def about(request):
    return render(request, 'resources/about.html')

def gallery(request):
    return render(request, 'resources/gallery.html')

def contact(request):
    return render(request, 'resources/contact.html')

def faq(request):
    return render(request, 'resources/faq.html')

def devolopper(request):
    return render(request, 'resources/About_Devolopper.html')

def updateOrderStatus(request, order_id):
    if request.method == "POST":
        status = request.POST.get("status")
        order = get_object_or_404(Order, id=order_id)
        order.status = status
        order.save()
        messages.success(request, f"Order status updated to {status}")
        return redirect('some_view_to_redirect_to')
    else:
        return redirect('some_view_to_redirect_to')

def account_info(request):
    if not request.user.is_authenticated:
        return redirect('auth_app:loginOrRegister')

    customer = request.user.customer
    last_shipping = ShippingAddress.objects.filter(customer=customer).order_by('-date_added').first()

    context = {
        'user': request.user,
        'shipping_info': last_shipping,
    }
    return render(request, 'store/account_info.html', context)

def add_to_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('productId')

        if request.user.is_authenticated:
            product = Product.objects.get(id=product_id)
            wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
            if not created:
                wishlist_item.delete()
                added = False
            else:
                added = True
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        else:
            wishlist = json.loads(request.COOKIES.get('wishlist', '{}'))
            if str(product_id) in wishlist:
                del wishlist[str(product_id)]
                added = False
            else:
                wishlist[str(product_id)] = True
                added = True
            wishlist_count = len(wishlist)

        response = JsonResponse({'added': added, 'wishlist_count': wishlist_count})

        if not request.user.is_authenticated:
            response.set_cookie('wishlist', json.dumps(wishlist))

        return response

    return JsonResponse({'error': 'Invalid request'}, status=400)

def remove_from_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('productId')

        if request.user.is_authenticated:
            product = Product.objects.get(id=product_id)
            wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
            if wishlist_item:
                wishlist_item.delete()
                removed = True
            else:
                removed = False
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        else:
            wishlist = json.loads(request.COOKIES.get('wishlist', '{}'))
            if str(product_id) in wishlist:
                del wishlist[str(product_id)]
                removed = True
            else:
                removed = False
            wishlist_count = len(wishlist)

        response = JsonResponse({'removed': removed, 'wishlist_count': wishlist_count})

        if not request.user.is_authenticated:
            response.set_cookie('wishlist', json.dumps(wishlist))

        return response

    return JsonResponse({'error': 'Invalid request'}, status=400)


def wishlist(request):
    wishlist_items = []

    if request.user.is_authenticated:
        # Fetch wishlist items for authenticated users
        wishlist_objects = Wishlist.objects.filter(user=request.user)
        for item in wishlist_objects:
            wishlist_items.append({
                'id': item.product.id,
                'name': item.product.name,
                'stock': item.product.stock,
                'image_url': item.product.imageURL,
                'new_price': item.product.new_price,
                'old_price': item.product.old_price,
                'get_url': item.product.get_url(),
                'discount_percentage': item.product.get_discounted_price if item.product.old_price != None and item.product.old_price != 0 else None,
            })
    else:
        # Use cookie data for unauthenticated users
        cookie_data = cookieWishlist(request)
        wishlist_items = cookie_data['wishlist_items']
        for item in wishlist_items:
            item['discount_percentage'] = (
                int(round(((item['old_price'] - item['new_price']) / item['old_price']) * 100))
                if item['old_price'] and item['new_price'] < item['old_price']
                else None
            )

    wishlist_count = len(wishlist_items)

    return render(request, 'store/Wishlist.html', {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
    })

def is_product_in_wishlist(request, product):
    if request.user.is_authenticated:
        return Wishlist.objects.filter(user=request.user, product=product).exists()
    else:
        cookie_data = cookieWishlist(request)
        return str(product.id) in cookie_data['wishlist_items']

@login_required
def trackOrder(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    order_items = OrderItem.objects.filter(order=order)
    shipping_address = ShippingAddress.objects.filter(order=order).first()

    context = {
        'order': order,
        'order_items': order_items,
        'shipping_address': shipping_address,
    }
    return render(request, 'store/trackOrder.html', context)