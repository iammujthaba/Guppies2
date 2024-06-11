from django.contrib import messages,auth
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

from store.models import Customer


# Create your views here.
def login(request):
    if request.method == 'POST':
        login_input = request.POST['login_input']
        password = request.POST['password']

        # Check if the login_input is an email
        if User.objects.filter(email=login_input).exists():
            user = User.objects.get(email=login_input)
            username = user.username
        else:
            username = login_input

        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'invalid credential')
            return redirect('auth_app:login')
    return render(request,'login.html')
    

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

