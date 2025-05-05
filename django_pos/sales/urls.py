from django.urls import path

from . import views

app_name = "sales"
urlpatterns = [
    path('', views.sales_list_view, name='sales_list'),
    path('customer', views.sales_list_customer_view, name='sales_list_customer'),
    path('add', views.sales_add_view, name='sales_add'),
    path('details/<str:sale_id>', views.sales_details_view, name='sales_details'),
    path('details_customer/<str:sale_id>', views.sales_details_customer, name='sales_details_customer'),
    path("pdf/<str:sale_id>", views.receipt_pdf_view, name="sales_receipt_pdf"),
]
