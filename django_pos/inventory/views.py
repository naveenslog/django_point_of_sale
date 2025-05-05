import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from inventory.models import RawMaterial, Inventory, Ledger, Worker
from inventory.forms import RawMaterialForm, TransactionForm
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from inventory.services import create_material_and_order
from langchain.chat_models import ChatOpenAI
from django.views.decorators.http import require_POST
from django.conf import settings

from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from inventory.services import create_material_and_order
from pydantic import BaseModel, Field
from typing import Optional

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def material_list_view(request):
    materials = RawMaterial.objects.all()
    context = {
        "active_icon": "inventory",
        "materials": materials,
    }
    return render(request, "inventory/material_list.html", context=context)

@login_required
def material_list(request):
    materials = RawMaterial.objects.all()
    transactions = Ledger.objects.select_related('material', 'worker').order_by('-date')
    
    context = {
        "active_icon": "inventory",
        "materials": materials,
        "transactions": transactions,
    }

    return render(request, "inventory/material_list.html", context=context)


@login_required
def material_add_view(request):
    context = {
        "active_icon": "inventory",
    }

    if request.method == 'POST':
        form = RawMaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material created successfully!', extra_tags="success")
            return redirect('inventory:material_list')
        else:
            messages.error(request, 'There was an error with your submission!', extra_tags="danger")
    else:
        form = RawMaterialForm()

    context['form'] = form
    return render(request, "inventory/material_add.html", context=context)

@login_required
def material_details_view(request, material_id):
    material = get_object_or_404(RawMaterial, id=material_id)
    transactions = Ledger.objects.filter(material=material).order_by('-date')
    inventory = Inventory.objects.filter(material=material).first()
    
    context = {
        "active_icon": "inventory",
        "material": material,
        "transactions": transactions,
        "inventory": inventory,
    }
    return render(request, "inventory/material_details.html", context=context)

@login_required
def inventory_list_view(request):
    inventory_items = Inventory.objects.select_related('material').all()
    
    # Calculate low stock items (less than 10 units)
    low_stock = inventory_items.filter(stock_quantity__lt=10)
    
    context = {
        "active_icon": "inventory",
        "inventory_items": inventory_items,
        "low_stock": low_stock,
    }
    return render(request, "inventory/inventory_list.html", context=context)

@login_required
def transaction_list_view(request):
    transactions = Ledger.objects.select_related('material', 'worker').all().order_by('-date')
    
    context = {
        "active_icon": "inventory",
        "transactions": transactions,
    }
    return render(request, "inventory/transaction_list.html", context=context)

@login_required
def transaction_add_view(request):
    context = {
        "active_icon": "inventory",
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            try:
                data = json.load(request)
                
                worker = Worker.objects.get(id=int(data['worker']))
                material = RawMaterial.objects.get(id=int(data['material']))
                
                transaction = Ledger.objects.create(
                    worker=worker,
                    material=material,
                    quantity=float(data['quantity']),
                    transaction_type=data['transaction_type'],
                    purpose=data.get('purpose', ''),
                )
                
                messages.success(request, 'Transaction recorded successfully!', extra_tags="success")
                return JsonResponse({'status': 'success'})
                
            except Exception as e:
                messages.error(request, f'Error recording transaction: {str(e)}', extra_tags="danger")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
        else:
            form = TransactionForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Transaction recorded successfully!', extra_tags="success")
                return redirect('inventory:transaction_list')
            else:
                messages.error(request, 'There was an error with your submission!', extra_tags="danger")
    else:
        form = TransactionForm()

    context['form'] = form
    context['workers'] = Worker.objects.all()
    context['materials'] = RawMaterial.objects.all()
    return render(request, "inventory/transaction_add.html", context=context)

@login_required
def transaction_details_view(request, transaction_id):
    transaction = get_object_or_404(Ledger, id=transaction_id)
    
    context = {
        "active_icon": "inventory",
        "transaction": transaction,
    }
    return render(request, "inventory/transaction_details.html", context=context)

@login_required
def get_materials(request):
    if is_ajax(request):
        search_term = request.POST.get('term', '')
        
        materials = RawMaterial.objects.filter(name__icontains=search_term).values('id', 'name', 'unit_of_measurement')
        
        results = []
        for material in materials:
            results.append({
                'id': material['id'],
                'text': f"{material['name']} ({material['unit_of_measurement']})",
                'name': material['name'],
                'unit': material['unit_of_measurement'],
            })
        
        return JsonResponse(results, safe=False)
    
    return JsonResponse({'error': 'Not Ajax request'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_create_material_and_order(request):
    try:
        data = json.loads(request.body)
        result = create_material_and_order(data)
        
        if result['status'] == 'success':
            return JsonResponse(result, status=201)
        else:
            return JsonResponse(result, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON data"
        }, status=400)


class OrderSchema(BaseModel):
    material_name: str = Field(..., description="The name of the raw material")
    description: Optional[str] = Field(None, description="A short description of the material")
    quantity: float = Field(..., description="The quantity to order")
    unit_of_measurement: str = Field(
        ..., 
        description="Unit of measurement (e.g. kg, g, liters, ml, pieces, boxes, units)"
    )
    purpose: Optional[str] = Field(None, description="The purpose of this order")


@require_POST
@csrf_exempt
def ai_process_order(request):
    parser = PydanticOutputParser(pydantic_object=OrderSchema)
    raw_materials_list = list(RawMaterial.objects.all().values_list("name", flat=True))

    units_of_measurement = ["kg", "g", "liters", "ml", "pieces", "boxes", "units"]

    materials_string = ", ".join(raw_materials_list)
    units_string = ", ".join(units_of_measurement)

    prompt = ChatPromptTemplate.from_messages([
        ("system", 
        f"""You're a helpful assistant that extracts structured data from raw food order instructions.
        
        Follow these STRICT rules:
        1. **Material Name** must exactly match one of these predefined materials: {materials_string}.
        2. **Unit of Measurement** must exactly match one of these options: {units_string}.
        3. Do not create new materials or units.
        4. If quantity is missing, assume it is 1.
        5. If purpose is missing, leave it empty.

        Format the output as instructed.

        """
        ),
        ("human", "Extract details from this order text: {order_text}\n{format_instructions}")
    ])
    data = json.loads(request.body)
    order_text = data.get('order_text', '').strip()
    
    if not order_text:
        return JsonResponse({'status': 'error', 'message': 'No order text provided'})

    llm = ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model="gpt-3.5-turbo",
        temperature=0
    )
    formatted_prompt = prompt.format_messages(
        order_text=order_text,
        format_instructions=parser.get_format_instructions()
    )
    llm_response = llm(formatted_prompt)
    parsed_data = parser.parse(llm_response.content)
    service_data = {
        "material": {
            "name": parsed_data.material_name,
            "description": parsed_data.description or '',
            "unit_of_measurement": parsed_data.unit_of_measurement
        },
        "order": {
            "quantity": parsed_data.quantity,
            'worker_id': request.user.id,
            "purpose": parsed_data.purpose or 'AI Voice Order'
        },
        "status": "success"
    }
    print(service_data, "service_dataservice_dataservice_dataservice_data")
    return JsonResponse(service_data)

@require_POST
@csrf_exempt
def ai_submit_order(request):
    data = json.loads(request.body)
    result = create_material_and_order(data)
    return JsonResponse(result)

@login_required
@require_POST
@csrf_exempt  # Optional if CSRF is handled via JavaScript
def update_transaction_status(request, transaction_id):
    try:
        transaction = Ledger.objects.get(id=transaction_id)
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status not in dict(Ledger.STATUS_CHOICES):
            return JsonResponse({'status': 'error', 'message': 'Invalid status'}, status=400)

        transaction.status = new_status
        transaction.save()

        return JsonResponse({'status': 'success', 'message': 'Transaction status updated successfully'})
    except Ledger.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
