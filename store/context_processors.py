from . models import Category
from . utils import cartData

def menu_link(request):
    links = Category.objects.all()
    return dict(links = links)

def cart_data(request):
    data = cartData(request)
    cartItems = data['cartItems']
    return dict(cartItems = cartItems)