import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_pos.wsgi import *
from django_pos import settings
from django.template.loader import get_template
from customers.models import Customer
from products.models import Product
from weasyprint import HTML, CSS
from .models import Sale, SaleDetail
import json


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url="/accounts/login/")
def sales_list_view(request):
    context = {
        "active_icon": "sales",
        "sales": Sale.objects.all()
    }
    return render(request, "sales/sales.html", context=context)


@login_required(login_url="/accounts/login/")
def sales_list_customer_view(request):
    customer = Customer.objects.filter(user_id=request.user.id).first()
    print(customer, "customercustomercustomercustomer")
    context = {
        "active_icon": "sales",
        "sales": Sale.objects.filter(customer=customer)
    }
    return render(request, "sales/sales_customer.html", context=context)

@login_required(login_url="/accounts/login/")
def sales_add_view(request):
    context = {
        "active_icon": "sales",
        "customers": [c.to_select2() for c in Customer.objects.all()]
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            data = json.load(request)
            tax_percentage = float(data.get('tax_percentage', settings.DEFAULT_TAX_PERCENTAGE))
            customer_id = data.get("customer", None)
            order_by = None
            if customer_id is not None:
                # Created by sales man
                order_by = "salesman"
                customer = Customer.objects.get(id=int(data['customer']))
            else:
                # Created by customer directly
                order_by = "customer"
                customer = Customer.objects.get(user_id=request.user.id)

            sale_attributes = {
                "customer": customer,
                "sub_total": float(data["sub_total"]),
                "grand_total": float(data["grand_total"]),
                "tax_amount": float(data["tax_amount"]),
                "tax_percentage": tax_percentage,
                "amount_payed": float(data["amount_payed"]),
                "amount_change": float(data["amount_change"]),
            }
            try:
                new_sale = Sale.objects.create(**sale_attributes)
                new_sale.save()
                products = data["products"]

                for product in products:
                    detail_attributes = {
                        "sale": Sale.objects.get(id=new_sale.id),
                        "product": Product.objects.get(id=int(product["id"])),
                        "price": product["price"],
                        "quantity": product["quantity"],
                        "total_detail": product["total_product"]
                    }
                    sale_detail_new = SaleDetail.objects.create(**detail_attributes)
                    sale_detail_new.save()
                messages.success(request, 'Sale created successfully!', extra_tags="success")

            except Exception as e:
                messages.success(request, 'There was an error during the creation!', extra_tags="danger")
        if order_by == "salesman":
            return redirect('sales:sales_list')
        else:
            return redirect('sales:sales_list_customer')
    return render(request, "sales/sales_add.html", context=context)


@login_required(login_url="/accounts/login/")
def sales_details_view(request, sale_id):
    """
    Args:
        request:
        sale_id: ID of the sale to view
    """
    try:
        # Get the sale
        sale = Sale.objects.get(id=sale_id)

        # Get the sale details
        details = SaleDetail.objects.filter(sale=sale)

        context = {
            "active_icon": "sales",
            "sale": sale,
            "details": details,
        }
        return render(request, "sales/sales_details.html", context=context)
    except Exception as e:
        messages.success(
            request, 'There was an error getting the sale!', extra_tags="danger")
        print(e)
        return redirect('sales:sales_list')
    
@login_required(login_url="/accounts/login/")
def sales_details_customer(request, sale_id):
    """
    Args:
        request:
        sale_id: ID of the sale to view
    """
    try:
        # Get the sale
        sale = Sale.objects.get(id=sale_id)

        # Get the sale details
        details = SaleDetail.objects.filter(sale=sale)

        context = {
            "active_icon": "sales",
            "sale": sale,
            "details": details,
        }
        return render(request, "sales/sales_details_customer.html", context=context)
    except Exception as e:
        messages.success(request, 'There was an error getting the sale!', extra_tags="danger")
        return redirect('sales:sales_list')


@login_required(login_url="/accounts/login/")
def receipt_pdf_view(request, sale_id):
    """
    Args:
        request:
        sale_id: ID of the sale to view the receipt
    """
    # Get the sale
    sale = Sale.objects.get(id=sale_id)

    # Get the sale details
    details = SaleDetail.objects.filter(sale=sale)

    template = get_template("sales/sales_receipt_pdf.html")
    context = {
        "sale": sale,
        "details": details
    }
    html_template = template.render(context)

    # CSS Boostrap
    css_url = os.path.join(
        settings.BASE_DIR, 'static/css/receipt_pdf/bootstrap.min.css')

    # Create the pdf
    pdf = HTML(string=html_template).write_pdf(stylesheets=[CSS(css_url)])

    return HttpResponse(pdf, content_type="application/pdf")
