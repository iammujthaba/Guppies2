from django.contrib import messages,auth
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

from store.models import Product, Order, OrderItem, Customer
import json

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

                    if product.available and product.stock >= (quantity + order_item.quantity):
                        order_item.quantity += quantity
                        order_item.save()
                        success_messages.add("Your Cookies Cart items added into your Cart.")
                    else:
                        if not product.available:
                            info_messages.add(f"The product {product.name} is no longer available.")
                        if product.stock < (quantity + order_item.quantity):
                            info_messages.add(f"The product {product.name} does not have enough stock. Available stock: {product.stock}, Requested quantity: {quantity + order_item.quantity}")

                except OrderItem.DoesNotExist:
                    if product.available and product.stock >= quantity:
                        OrderItem.objects.create(order=order, product=product, quantity=quantity)
                        success_messages.add("Your Cookies Cart items added into your Cart.")
                    else:
                        if not product.available:
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
                    messages.info(request, f"Your cart has {total_quantity} quantities waiting to complete the order 😊")
                else:
                    messages.info(request, "Your cart is empty.")
            else:
                messages.info(request, "Your cart is empty.")
        except Order.DoesNotExist:
            messages.info(request, "Your cart is empty.")

        return redirect('/')

# Add the merge_cookie_cart_with_user_cart function call in your login view
def login(request):
    if request.method == 'POST':
        login_input = request.POST['login_input']
        password = request.POST['password']

        if User.objects.filter(email=login_input).exists():
            user = User.objects.get(email=login_input)
            username = user.username
        else:
            username = login_input

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            response = merge_cookie_cart_with_user_cart(request, user)
            return response
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('auth_app:login')

    return render(request, 'login.html')
    

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        c_password = request.POST['password2']
        if password == c_password:
            if User.objects.filter(username = username).exists():
                messages.info(request,'Username is already taken')
            elif User.objects.filter(email = email).exists():
                messages.info(request,'E-mail is already taken')
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()
                Customer.objects.create(user=user,name=username,email=email)
                print('user is created...')
                return redirect('auth_app:login')
                
        else:
            messages.info(request,'Pssword is no\'t match')
        return redirect('auth_app:register')
    return render(request,'register.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def loginOrRegister(request):
    return redirect(request,'loginOrRegister.html')

