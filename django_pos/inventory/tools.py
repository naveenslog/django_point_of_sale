from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
from .services import create_material_and_order

class MaterialOrderInput(BaseModel):
    material_name: str = Field(..., description="The name of the raw material")
    description: Optional[str] = Field(None, description="Description of the material")
    quantity: float = Field(..., description="Quantity to order")
    unit_of_measurement: str = Field(
        ..., 
        description="Unit of measurement", 
        enum=["kg", "g", "liters", "ml", "pieces", "boxes", "units"]
    )
    purpose: Optional[str] = Field(None, description="Purpose of the order")

class MaterialOrderTool(BaseTool):
    name: str = "create_material_order"
    description: str = "Create a new raw material or order an existing one"
    args_schema: type = MaterialOrderInput

    def _run(self, material_name: str, quantity: float, unit_of_measurement: str, description: str = None, purpose: str = None):
        order_data = {
            'material': {
                'name': material_name,
                'description': description or '',
                'unit_of_measurement': unit_of_measurement
            },
            'order': {
                'quantity': quantity,
                'purpose': purpose or 'AI Voice Order'
            }
        }
        return create_material_and_order(order_data)

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async operation not supported")
