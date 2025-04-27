# inventory/services.py
from django.db import transaction
from .models import RawMaterial, Inventory, Ledger, Worker
from django.contrib.auth import get_user_model

User = get_user_model()

def create_material_and_order(json_data):
    """
    Creates a raw material (if it doesn't exist) and places an order for it.
    
    Expected JSON format:
    {
        "material": {
            "name": "Flour",
            "description": "All-purpose flour",
            "unit_of_measurement": "kg"
        },
        "order": {
            "quantity": 50.0,
            "worker_id": 1,  # Optional
            "purpose": "Regular stock replenishment"  # Optional
        }
    }
    
    Returns:
        dict: {
            "status": "success" or "error",
            "message": "Detailed message",
            "material": material_object,
            "transaction": transaction_object
        }
    """
    # try:
    with transaction.atomic():  # Ensure all operations succeed or fail together
        # Step 1: Get or create the raw material
        material_data = json_data.get('material', {})
        if not material_data:
            return {
                "status": "error",
                "message": "Material data is required"
            }
        
        material, created = RawMaterial.objects.get_or_create(
            name=material_data['name'],
            defaults={
                'description': material_data.get('description', ''),
                'unit_of_measurement': material_data['unit_of_measurement']
            }
        )
        
        # Step 2: Prepare order data
        order_data = json_data.get('order', {})
        if not order_data:
            return {
                "status": "error",
                "message": "Order data is required"
            }
        
        quantity = float(order_data['quantity'])
        if quantity <= 0:
            return {
                "status": "error",
                "message": "Quantity must be positive"
            }
        
        # Step 3: Get worker (if specified)
        worker = None
        if 'worker_id' in order_data:
            try:
                worker = Worker.objects.filter(user_id=order_data['worker_id']).first()
                if worker is None:
                    worker = Worker.objects.create(user_id=order_data['worker_id'], role="chef")
            except Worker.DoesNotExist:
                return {
                    "status": "error",
                    "message": "Worker not found"
                }
        
        print(material, "statsdfkhsdflkjsdhkfhjsdfkhsdfkhsdfkhsdf")
        # Step 4: Create the order transaction
        transaction_obj = Ledger.objects.create(
            worker=worker,
            material=material,
            quantity=quantity,
            transaction_type='order',
            purpose=order_data.get('purpose', '')
        )

        print(transaction_obj)
        
        print(material, "444444444444444444444444444444444444444444444444")
        # Step 5: Update inventory
        # inventory = Inventory.objects.filter(material=material).first()
        # if inventory is None:
        #     Inventory.objects.create(
        #         material=material,
        #         stock_quantity=quantity
        #     )
        # else:
        #     inventory.stock_quantity += quantity
        #     inventory.save()
        
        return {
            "status": "success",
            "message": f"{'Created new' if created else 'Found existing'} material and placed order",
            "material": {
                "id": material.id,
                "name": material.name,
                "unit": material.unit_of_measurement
            },
            "transaction": {
                "id": transaction_obj.id,
                "quantity": transaction_obj.quantity,
                "date": transaction_obj.date
            }
        }
        
    # except KeyError as e:
    #     return {
    #         "status": "error",
    #         "message": f"Missing required field: {str(e)}"
    #     }
    # except Exception as e:
    #     return {
    #         "status": "error",
    #         "message": f"An error occurred: {str(e)}"
    #     }