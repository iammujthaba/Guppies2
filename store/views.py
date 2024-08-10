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

logger = logging.getLogger(__name__)

def allProdCat(request, c_slug=None):
    c_page = None
    offer = None
    products_list = None
    intro_images = IntroImage.objects.all()  # Move this line outside the if-else block

    if c_slug is not None:
        print('c_slug...........',c_slug)
        c_page = get_object_or_404(Category, slug=c_slug)
        print('c_page...........',c_page)
        products_list = Product.objects.all().filter(category=c_page, active=True, stock__gt=0)
    else:
        products_list = Product.objects.all().filter(active=True, stock__gt=0)

    offer_list = Product.objects.filter(active=True, old_price__gt=0)

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
        'intro_images': intro_images,
        'messages': message_list
    })

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    total_price_difference = data['total_price_difference']

    # Calculate price_difference for each item
    if request.user.is_authenticated:
        for item in items:
            item.product.price_difference = item.product.old_price - item.product.new_price
    else:
        for item in items:
            item['product']['price_difference'] = item['product']['old_price'] - item['product']['new_price']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'total_price_difference': total_price_difference
    }
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        data = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']

        # Get the last shipping information
        customer = request.user.customer
        last_shipping = ShippingAddress.objects.filter(customer=customer).order_by('-date_added').first()

        context = {
            'items': items,
            'order': order,
            'cartItems': cartItems,
            'last_shipping': last_shipping,
        }
        return render(request, 'store/checkout.html', context)
    else:
        return render(request, 'auth_app/loginOrRegister.html')

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
    total_price_difference = sum((item.product.old_price - item.product.new_price) * item.quantity for item in order.orderitem_set.all())

    return JsonResponse({
        'added': added,
        'message': message,
        'cartItems': cart_items,
        'cartTotal': cart_total,
        'totalPriceDifference': total_price_difference,
        'itemQuantity': orderItem.quantity if orderItem.id else 0,
        'itemTotal': orderItem.get_total if orderItem.id else 0,
    }, safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = data['shipping']['total']
        order.transaction_id = transaction_id
        
        if total == str(order.get_cart_total):
            order.complete = True
            order.save()
            
            # Decrement stock for each product in the order
            for item in order.orderitem_set.all():
                if item.price_at_purchase is None:
                    item.price_at_purchase = item.product.new_price
                item.save()
                
                # Decrement product stock
                product = item.product
                product.stock -= item.quantity
                product.save()
                
                # Record purchase history
                PurchaseHistory.objects.create(
                    customer=customer,
                    product=product,
                    price_at_purchase=item.price_at_purchase
                )
                
            # Save shipping address
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                number=data['shipping']['number'],
                whatsapp=data['shipping']['whatsapp'],
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
                date_added=timezone.now()
            )
            
            success = True
            message = "Transaction completed, \nYour order placed successfully..."
        else:
            success = False
            message = "Something went wrong! \nOrder not placed, For more contact us."
        
        return JsonResponse({'success': success, 'message': message}, safe=False)




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
        return render(request, 'auth_app/loginOrRegister.html')
    
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
    products_list = Product.objects.all().filter(active=True)
    paginator = Paginator(products_list, 14)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        products = paginator.page(page)
    except (InvalidPage, EmptyPage):
        products = paginator.page(paginator.num_pages)
    return render(request, 'store/shop.html', {'products': products})

def offerProductListing(request):
    products_list = Product.objects.filter(old_price__gt=0)
    paginator = Paginator(products_list, 14)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        products = paginator.page(page)
    except (InvalidPage, EmptyPage):
        products = paginator.page(paginator.num_pages)
    return render(request, 'store/shop.html', {'products': products})

def Category_list(request):
    categorys_list = Category.objects.all()
    return render(request, 'store/category_listing.html', {'categorys_list': categorys_list})

def orders(request):
    if not request.user.is_authenticated:
        return redirect('auth_app:login')
    
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer, complete=True)
    pending_orders = orders.exclude(status='Delivered')
    delivered_orders = orders.filter(status='Delivered')
    
    context = {
        'user': request.user,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
    }
    return render(request, 'store/orders.html', context)

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
                'discount_percentage': item.product.get_discounted_price if item.product.old_price > 0 else None,
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

    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
    })

def is_product_in_wishlist(request, product):
    if request.user.is_authenticated:
        return Wishlist.objects.filter(user=request.user, product=product).exists()
    else:
        cookie_data = cookieWishlist(request)
        return str(product.id) in cookie_data['wishlist_items']
