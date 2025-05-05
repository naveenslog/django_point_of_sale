from django.urls import path

from . import views

app_name = "customers"
urlpatterns = [
    path('', views.customers_list_view, name='customers_list'),
    path('quick-register/', views.quick_register_view, name='quick_register'),
    path('add', views.customers_add_view, name='customers_add'),
    path('update/<str:customer_id>', views.customers_update_view, name='customers_update'),
    path('delete/<str:customer_id>', views.customers_delete_view, name='customers_delete'),
]
