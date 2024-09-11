from django.shortcuts import render, get_object_or_404, redirect
from .forms import CategoryForm, ProductForm, ShippingRateForm
from store.models import Category, OrderItem, Product, Order, Customer, ShippingAddress, ShippingRate
from django.db.models import Count, Q, Sum, F, FloatField
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_superuser

# @login_required
# @user_passes_test(is_admin)
# def dashboard(request):
#     return render(request, 'admin_app/dashboard.html')
@login_required
@user_passes_test(is_admin)
def dashboard(request):
    total_categories = Category.objects.count()
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    processing_orders_count = Order.objects.filter(status='Processing').count()
    confirmed_orders_count = Order.objects.filter(status='Confirmed').count()
    shipped_orders_count = Order.objects.filter(status='Shipped').count()
    delivered_orders_count = Order.objects.filter(status='Delivered').count()
    total_revenue = OrderItem.objects.filter(order__complete=True).aggregate(
        total_revenue=Sum(F('price_at_purchase') * F('quantity'), output_field=FloatField())
    )['total_revenue'] or 0
    
    context = {
        'total_categories': total_categories,
        'total_products': total_products,
        'processing_orders_count': processing_orders_count,
        'confirmed_orders_count': confirmed_orders_count,
        'shipped_orders_count': shipped_orders_count,
        'delivered_orders_count': delivered_orders_count,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
    }

    return render(request, 'admin_app/dashboard.html', context)

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
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    
    if selected_category:
        products = Product.objects.filter(category_id=selected_category)
    else:
        products = Product.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'admin_app/product_list.html', context)

@login_required
@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.clean()  # Run model validation
            product.save()
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
            product = form.save(commit=False)
            product.clean()  # Run model validation
            product.save()
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

# @login_required
# @user_passes_test(is_admin)
# def order_list(request):
#     orders = Order.objects.filter(Q(complete=True) & ~Q(status='Delivered'))
#     return render(request, 'admin_app/order_list.html', {'orders': orders})

@login_required
@user_passes_test(is_admin)
def order_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    shipping_address = ShippingAddress.objects.filter(order=order).first()
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status != order.status:
            order.status = new_status
            order.save()
        return redirect('admin_app:order_view', pk=pk)
    return render(request, 'admin_app/order_view.html', {
        'order': order,
        'shipping_address': shipping_address
    })



@login_required
@user_passes_test(is_admin)
def shipping_rate_list(request):
    shipping_rates = ShippingRate.objects.all()
    return render(request, 'admin_app/shipping_rate_list.html', {'shipping_rates': shipping_rates})

@login_required
@user_passes_test(is_admin)
def shipping_rate_create(request):
    if request.method == 'POST':
        form = ShippingRateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_app:shipping_rate_list')
    else:
        form = ShippingRateForm()
    return render(request, 'admin_app/shipping_rate_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def shipping_rate_update(request, pk):
    shipping_rate = get_object_or_404(ShippingRate, pk=pk)
    if request.method == 'POST':
        form = ShippingRateForm(request.POST, instance=shipping_rate)
        if form.is_valid():
            form.save()
            return redirect('admin_app:shipping_rate_list')
    else:
        form = ShippingRateForm(instance=shipping_rate)
    return render(request, 'admin_app/shipping_rate_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def shipping_rate_delete(request, pk):
    shipping_rate = get_object_or_404(ShippingRate, pk=pk)
    if request.method == 'POST':
        shipping_rate.delete()
        return redirect('admin_app:shipping_rate_list')
    return render(request, 'admin_app/shipping_rate_confirm_delete.html', {'shipping_rate': shipping_rate})


@login_required
@user_passes_test(is_admin)
def processing_orders(request):
    orders = Order.objects.filter(complete=True, status='Processing')
    return render_order_list(request, orders, 'Processing Orders', 'admin_app/order_list.html')

@login_required
@user_passes_test(is_admin)
def confirmed_orders(request):
    orders = Order.objects.filter(complete=True, status='Confirmed')
    return render_order_list(request, orders, 'Confirmed Orders', 'admin_app/order_list.html')

@login_required
@user_passes_test(is_admin)
def shipped_orders(request):
    orders = Order.objects.filter(complete=True, status='Shipped')
    return render_order_list(request, orders, 'Shipped Orders', 'admin_app/order_list.html')

@login_required
@user_passes_test(is_admin)
def completed_orders(request):
    orders = Order.objects.filter(complete=True, status='Delivered')
    return render_order_list(request, orders, 'Completed Orders', 'admin_app/order_list.html')

def render_order_list(request, orders, title, template):
    orders_with_details = []
    for order in orders:
        shipping_address = ShippingAddress.objects.filter(order=order).first()
        total_quantity = OrderItem.objects.filter(order=order).aggregate(Sum('quantity'))['quantity__sum']
        orders_with_details.append({
            'order': order,
            'state': shipping_address.state if shipping_address else 'N/A',
            'total_quantity': total_quantity or 0
        })
    return render(request, template, {'orders_with_details': orders_with_details, 'title': title})


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