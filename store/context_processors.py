from . models import Category
from . utils import cartData
from django.core.paginator import Paginator,EmptyPage,InvalidPage

def menu_link(request):
    links_list = Category.objects.all()

    paginator3 = Paginator(links_list,8)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1

    try:
        links = paginator3.page(page)
    except (InvalidPage,EmptyPage):
        links = paginator3.page(paginator3.num_pages)

    return dict(links = links)

def cart_data(request):
    data = cartData(request)
    cartItems = data['cartItems']
    return dict(cartItems = cartItems)