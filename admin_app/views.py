from django.shortcuts import render, get_object_or_404, redirect
from .forms import CategoryForm, ProductForm
from store.models import Category, OrderItem, Product, Order, Customer, ShippingAddress
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    return render(request, 'admin_app/dashboard.html')

# Apply the same decorators to the other views

@login_required
@user_passes_test(is_admin)
def category_list(request):
    # categories = Category.objects.all()
    categories = Category.objects.annotate(num_products=Count('product')).all()
    return render(request, 'admin_app/category_list.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_app:category_list')
    else:
        form = CategoryForm()
    return render(request, 'admin_app/category_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('admin_app:category_list')
    else:
        # get exact admin panal
        form = CategoryForm(instance=category)
    return render(request, 'admin_app/category_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('admin_app:category_list')
    return render(request, 'admin_app/category_confirm_delete.html', {'category': category})

@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'admin_app/product_list.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_app:product_list')
    else:
        form = ProductForm()
    return render(request, 'admin_app/product_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_app:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_app/product_form.html', {'form': form})

# @login_required
# @user_passes_test(is_admin)
# def product_delete(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     if request.method == 'POST':
#         product.delete()
#         return redirect('admin_app:product_list')
#     return render(request, 'admin_app/product_confirm_delete.html', {'product': product})

@login_required
@user_passes_test(is_admin)
def order_list(request):
    orders = Order.objects.filter(Q(complete=True) & ~Q(status='Delivered'))
    return render(request, 'admin_app/order_list.html', {'orders': orders})

@login_required
@user_passes_test(is_admin)
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    shipping_address = ShippingAddress.objects.filter(order=order).first()
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status != order.status:
            order.status = new_status
            order.save()
            return redirect('admin_app:order_detail', pk=pk)
    
    return render(request, 'admin_app/order_detail.html', {
        'order': order,
        'shipping_address': shipping_address
    })


@login_required
@user_passes_test(is_admin)
def order_compleated_list(request):
    orders = Order.objects.filter(complete=True, status='Delivered').select_related('customer')

    for order in orders:
        order.shipping_address = ShippingAddress.objects.filter(order=order).first()
        order.total_quantity = OrderItem.objects.filter(order=order).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    return render(request, 'admin_app/order_compleated_list.html', {'orders': orders})


@login_required
@user_passes_test(is_admin)
def users_list(request):
    total_users = Customer.objects.all()
    complete_orders = Order.objects.filter(complete=True)
    customer_ids_with_complete_orders = set(complete_orders.values_list('customer_id', flat=True))
    customers_with_complete_orders = Customer.objects.filter(id__in=customer_ids_with_complete_orders)
    only_users = total_users.exclude(id__in=customer_ids_with_complete_orders)
    return render(request, 'admin_app/users_list.html', {
        'total_users': total_users,
        'customers_with_complete_orders': customers_with_complete_orders,
        'only_users': only_users
    })