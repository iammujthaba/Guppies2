from django import forms
from django.contrib import messages,auth
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

from store.models import Product, Order, OrderItem, Customer, Wishlist
from .forms import RegistrationForm, LoginForm, SuperuserPasswordForm
from django.contrib.auth import authenticate, login as auth_login
import json


SUPERUSER_CONTACT_NUMBER = '1234567890'
PREDEFINED_SUPERUSER_PASSWORD = '1234'

# Create your views here.
def merge_cookie_cart_with_user_cart(request, user):
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except json.JSONDecodeError:
        cart = {}

    if cart:
        customer = user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        success_messages = set()
        info_messages = set()
        error_messages = set()

        for product_id, cart_item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                quantity = cart_item['quantity']

                try:
                    order_item = OrderItem.objects.get(order=order, product=product)

                    if product.active and product.stock >= (quantity + order_item.quantity):
                        order_item.quantity += quantity
                        order_item.save()
                        success_messages.add("Your Cookies Cart items added into your Cart.")
                    else:
                        if not product.active:
                            info_messages.add(f"The product {product.name} is no longer available.")
                        if product.stock < (quantity + order_item.quantity):
                            info_messages.add(f"The product {product.name} does not have enough stock. Available stock: {product.stock}, Requested quantity: {quantity + order_item.quantity}")

                except OrderItem.DoesNotExist:
                    if product.active and product.stock >= quantity:
                        OrderItem.objects.create(order=order, product=product, quantity=quantity)
                        success_messages.add("Your Cookies Cart items added into your Cart.")
                    else:
                        if not product.active:
                            info_messages.add(f"The product {product.name} is no longer available.")
                        if product.stock < quantity:
                            info_messages.add(f"The product {product.name} does not have enough stock. Available stock: {product.stock}, Requested quantity: {quantity}")

            except Product.DoesNotExist:
                error_messages.add(f"Product with ID {product_id} does not exist.")

        for message in success_messages:
            messages.success(request, message)
        for message in info_messages:
            messages.info(request, message)
        for message in error_messages:
            messages.error(request, message)

        # Clear the cart cookie after merging
        response = redirect('/')
        response.delete_cookie('cart')
        return response

    else:
        customer = user.customer
        try:
            order = Order.objects.get(customer=customer, complete=False)
            order_items = OrderItem.objects.filter(order=order)
            if order_items.exists():
                total_quantity = sum(item.quantity for item in order_items)
                if total_quantity > 0:
                    messages.info(request, f"Your cart has {total_quantity} quantities waiting to complete the order.")
        except Order.DoesNotExist:
            messages.info(request, "Your cart is empty.")

        return None

def merge_cookie_wishlist_with_user_wishlist(request, user):
    try:
        cookie_wishlist = json.loads(request.COOKIES.get('wishlist', '{}'))
    except json.JSONDecodeError:
        cookie_wishlist = {}

    for product_id in cookie_wishlist:
        try:
            product = Product.objects.get(id=product_id)
            Wishlist.objects.get_or_create(user=user, product=product)
        except Product.DoesNotExist:
            pass

    response = redirect('store_app:allProdCat')
    response.delete_cookie('wishlist')
    return response


# Add the merge_cookie_cart_with_user_cart function call in your login view
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            contact_number = form.cleaned_data['contact_number']
            if contact_number == SUPERUSER_CONTACT_NUMBER:
                return redirect('auth_app:superuser_password')
            else:
                try:
                    customer = Customer.objects.get(contact_number=contact_number)
                    user = customer.user
                    auth_login(request, user)
                    
                    # Merge cookie cart with user cart
                    cart_response = merge_cookie_cart_with_user_cart(request, user)
                    
                    # Merge cookie wishlist with user wishlist
                    wishlist_response = merge_cookie_wishlist_with_user_wishlist(request, user)
                    
                    # Determine which response to return
                    if cart_response:
                        return cart_response
                    elif wishlist_response:
                        return wishlist_response
                    else:
                        return redirect('/')
                except Customer.DoesNotExist:
                    form.add_error('contact_number', 'This number is not found')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def superuser_password(request):
    if request.method == 'POST':
        form = SuperuserPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']

            if password == PREDEFINED_SUPERUSER_PASSWORD:
                # Authenticate superuser
                superuser = Customer.objects.get(contact_number=SUPERUSER_CONTACT_NUMBER).user
                auth_login(request, superuser)
                return redirect('/')
            else:
                form.add_error('password', 'Incorrect superuser password')
    else:
        form = SuperuserPasswordForm()

    return render(request, 'superuser_password.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            contact_number = form.cleaned_data['contact_number']

            user = User.objects.create_user(username=username)
            Customer.objects.create(user=user, name=username, contact_number=contact_number)

            # Log in the newly registered user
            auth_login(request, user)

            # Merge cookies cart with user cart
            cart_response = merge_cookie_cart_with_user_cart(request, user)

            # Merge cookies wishlist with user wishlist
            wishlist_response = merge_cookie_wishlist_with_user_wishlist(request, user)

            if cart_response:
                return cart_response
            elif wishlist_response:
                return wishlist_response
            return redirect('auth_app:login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('auth_app:register')
    form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def logout(request):
    auth.logout(request)
    return redirect('/')

def loginOrRegister(request):
    return render(request, 'loginOrRegister.html')