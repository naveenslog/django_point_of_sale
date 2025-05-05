from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Customer
from django.contrib.auth import login
from tenant.models import TenantUser

@login_required(login_url="/accounts/login/")
def customers_list_view(request):
    context = {
        "active_icon": "customers",
        "customers": Customer.objects.all()
    }
    return render(request, "customers/customers.html", context=context)


@login_required(login_url="/accounts/login/")
def customers_add_view(request):
    context = {
        "active_icon": "customers",
    }

    if request.method == 'POST':
        # Save the POST arguments
        data = request.POST

        attributes = {
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "address": data['address'],
            "email": data['email'],
            "phone": data['phone'],
        }

        # Check if a customer with the same attributes exists
        if Customer.objects.filter(**attributes).exists():
            messages.error(request, 'Customer already exists!',
                           extra_tags="warning")
            return redirect('customers:customers_add')

        try:
            # Create the customer
            new_customer = Customer.objects.create(**attributes)

            # If it doesn't exist save it
            new_customer.save()

            messages.success(request, 'Customer: ' + attributes["first_name"] + " " +
                             attributes["last_name"] + ' created successfully!', extra_tags="success")
            return redirect('customers:customers_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the creation!', extra_tags="danger")
            print(e)
            return redirect('customers:customers_add')

    return render(request, "customers/customers_add.html", context=context)


@login_required(login_url="/accounts/login/")
def customers_update_view(request, customer_id):
    """
    Args:
        request:
        customer_id : The customer's ID that will be updated
    """

    # Get the customer
    try:
        # Get the customer to update
        customer = Customer.objects.get(id=customer_id)
    except Exception as e:
        messages.success(
            request, 'There was an error trying to get the customer!', extra_tags="danger")
        print(e)
        return redirect('customers:customers_list')

    context = {
        "active_icon": "customers",
        "customer": customer,
    }

    if request.method == 'POST':
        try:
            # Save the POST arguments
            data = request.POST

            attributes = {
                "first_name": data['first_name'],
                "last_name": data['last_name'],
                "address": data['address'],
                "email": data['email'],
                "phone": data['phone'],
            }

            # Check if a customer with the same attributes exists
            if Customer.objects.filter(**attributes).exists():
                messages.error(request, 'Customer already exists!',
                               extra_tags="warning")
                return redirect('customers:customers_add')

            customer = Customer.objects.get(id=customer_id)

            messages.success(request, '¡Customer: ' + customer.get_full_name() +
                             ' updated successfully!', extra_tags="success")
            return redirect('customers:customers_list')
        except Exception as e:
            messages.success(
                request, 'There was an error during the update!', extra_tags="danger")
            print(e)
            return redirect('customers:customers_list')

    return render(request, "customers/customers_update.html", context=context)


@login_required(login_url="/accounts/login/")
def customers_delete_view(request, customer_id):
    """
    Args:
        request:
        customer_id : The customer's ID that will be deleted
    """
    try:
        # Get the customer to delete
        customer = Customer.objects.get(id=customer_id)
        customer.delete()
        messages.success(request, '¡Customer: ' + customer.get_full_name() +
                         ' deleted!', extra_tags="success")
        return redirect('customers:customers_list')
    except Exception as e:
        messages.success(
            request, 'There was an error during the elimination!', extra_tags="danger")
        print(e)
        return redirect('customers:customers_list')

from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend  # Your custom backend (if you're using one)

def quick_register_view(request):
    context = {
        "active_icon": "customers",
    }

    if request.method == 'POST':
        data = request.POST

        name = data['name'].strip()
        phone = data['phone'].strip()
        order_type = data['order_type']
        address = data.get('address', '').strip()

        # Create fake email
        fake_email = name.lower().replace(" ", "") + phone + "@example.com"

        attributes = {
            "first_name": name,
            "last_name": '',
            "email": fake_email,
            "phone": phone,
            "address": address if order_type == 'home_delivery' else '',
        }

        # First check if customer exists
        customer = Customer.objects.filter(phone=phone).first()

        if customer:
            # Customer exists -> Log them in
            user = customer.user  # Assuming Customer has OneToOneField with User
            if user:
                # Specify the backend explicitly if you have multiple authentication backends
                login(request, user, backend='tenant.backends.TenantAwareAuthenticationBackend')
                messages.success(request, f'Welcome back, {name}!', extra_tags="success")
                return redirect('product_list')
            else:
                messages.error(request, 'User account linked to customer not found.', extra_tags="danger")
                return redirect('customers:quick_register')
        
        else:
            # Customer doesn't exist -> Create customer and user
            try:
                user = TenantUser.objects.create_user(
                    username=phone,
                    email=fake_email,
                    password=phone,
                    tenant=request.tenant,
                )

                new_customer = Customer.objects.create(
                    user=user,
                    **attributes
                )
                new_customer.save()

                # Specify the backend explicitly here too
                login(request, user, backend='tenant.backends.TenantAwareAuthenticationBackend')
                messages.success(request, f'Customer {name} registered and logged in successfully!', extra_tags="success")
                return redirect('product_list')
            except Exception as e:
                messages.error(request, 'There was an error during registration!', extra_tags="danger")
                print(e)
                return redirect('customers:quick_register')

    return render(request, "accounts/register.html", context=context)
