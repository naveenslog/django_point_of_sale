# inventory/urls.py
from django.urls import path
from . import views

app_name = "inventory"
urlpatterns = [
    path('', views.material_list, name='material_list'),
    path('materials/', views.material_list, name='material_list'),
    path('materials/add/', views.material_add_view, name='material_add'),
    path('materials/<int:material_id>/', views.material_details_view, name='material_details'),
    
    path('inventory/', views.inventory_list_view, name='inventory_list'),
    
    path('transactions/', views.transaction_list_view, name='transaction_list'),
    path('transactions/add/', views.transaction_add_view, name='transaction_add'),
    path('transactions/<int:transaction_id>/', views.transaction_details_view, name='transaction_details'),
    path('ai-process_order/', views.ai_process_order, name='ai_process_order'),
    path('ai-submit-order/', views.ai_submit_order, name='ai_submit_order'),
    path('update-transaction-status/<int:transaction_id>/', views.update_transaction_status, name='update_transaction_status'),
]