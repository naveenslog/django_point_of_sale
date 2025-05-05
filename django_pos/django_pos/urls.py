
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render
from products.models import Product, Category
from django.conf import settings

def product_list_view(request):
    products = Product.objects.select_related('category').filter(status='ACTIVE')
    categories = Category.objects.filter(status='ACTIVE')
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'DEFAULT_TAX_PERCENTAGE': settings.DEFAULT_TAX_PERCENTAGE,
        'tax_percentage': settings.DEFAULT_TAX_PERCENTAGE
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('', include('pos.urls')),
    path('products/', include('products.urls')),
    path('customers/', include('customers.urls')),
    path('sales/', include('sales.urls')),
    path('products-list/', product_list_view, name='product_list'),
    path('inventory/', include('inventory.urls')),
]
