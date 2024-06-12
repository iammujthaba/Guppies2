from django.contrib import messages,auth
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

from store.models import Customer

# from django.shortcuts import redirect
# from django.contrib import messages, auth
# from django.contrib.auth.models import User
from store.models import Product, Order, OrderItem
import json

# Create your views here.
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
            merge_cookie_cart_with_user_cart(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('auth_app:login')

    return render(request, 'login.html')

def merge_cookie_cart_with_user_cart(request, user):
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except json.JSONDecodeError:
        cart = {}

    if cart:
        customer = user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        for product_id, cart_item in cart.items():
            product = Product.objects.get(id=product_id)
            quantity = cart_item['quantity']

            order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
            if created:
                order_item.quantity = quantity
            else:
                order_item.quantity += quantity

            order_item.save()

        # Clear the cart cookie after merging
        response = redirect('/')
        response.delete_cookie('cart')
        return response
    

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

