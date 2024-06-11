from django.shortcuts import render
from store.models import Product
from django.db.models import Q

# Create your views here.
def SearchResult(request):
    products = None
    query = None
    if 'q' in request.GET:
        query = request.GET.get('q')
        products = Product.objects.all().filter(Q(name__contains = query) | Q(description__contains = query), available = True, stock__gt=0)
        return render(request, 'store/search.html',{'query':query,'products':products})