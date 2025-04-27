import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from inventory.models import RawMaterial, Inventory, Ledger, Worker
from inventory.forms import RawMaterialForm, TransactionForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from inventory.services import create_material_and_order
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from inventory.tools import MaterialOrderTool
from django.views.decorators.http import require_POST
from django.conf import settings

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

# AJAX view to get materials for select2
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

@csrf_exempt  # Only if this is an API endpoint, remove if you have proper CSRF handling
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

# inventory/views.py
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from inventory.services import create_material_and_order
from pydantic import BaseModel, Field
from typing import Optional


# Step 1: Define expected schema
class OrderSchema(BaseModel):
    material_name: str = Field(..., description="The name of the raw material")
    description: Optional[str] = Field(None, description="A short description of the material")
    quantity: float = Field(..., description="The quantity to order")
    unit_of_measurement: str = Field(
        ..., 
        description="Unit of measurement (e.g. kg, g, liters, ml, pieces, boxes, units)"
    )
    purpose: Optional[str] = Field(None, description="The purpose of this order")

# Step 2: Create the parser
parser = PydanticOutputParser(pydantic_object=OrderSchema)

# Step 3: Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You're a helpful assistant that extracts structured data from raw order instructions."),
    ("human", "Extract details from this order text: {order_text}\n{format_instructions}")
])


@require_POST
@csrf_exempt
def ai_process_order(request):
    # try:
        data = json.loads(request.body)
        order_text = data.get('order_text', '').strip()
        
        if not order_text:
            return JsonResponse({'status': 'error', 'message': 'No order text provided'})

        # Step 4: Initialize LLM
        llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0
        )

        # Step 5: Format the prompt and get response
        formatted_prompt = prompt.format_messages(
            order_text=order_text,
            format_instructions=parser.get_format_instructions()
        )
        llm_response = llm(formatted_prompt)

        # Step 6: Parse LLM response to extract structured data
        parsed_data = parser.parse(llm_response.content)

        print(parsed_data, "parsed_dataparsed_dataparsed_dataparsed_dataparsed_data")

        # Step 7: Prepare data for material/order service
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
        # Step 8: Call the service function
        # result = create_material_and_order(service_data)
        return JsonResponse(service_data)

@require_POST
@csrf_exempt
def ai_submit_order(request):
    data = json.loads(request.body)
    result = create_material_and_order(data)
    return JsonResponse(result)