
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render
from products.models import Product

def product_list_view(request):
    products = Product.objects.select_related('category').filter(status='ACTIVE')
    return render(request, 'products/product_list.html', {'products': products})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('', include('pos.urls')),
    path('products/', include('products.urls')),
    path('customers/', include('customers.urls')),
    path('sales/', include('sales.urls')),
    path('products-list/', product_list_view, name='product_list'),
]
