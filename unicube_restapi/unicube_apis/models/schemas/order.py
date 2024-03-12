from pydantic import BaseModel
from typing import List, Optional

# class Items(BaseModel):
#     name: str | None = None

class DummyProduct(BaseModel):
    contact_id: int
    price: float = 0.0
    type: int = 0
    desc: str | None = None
    fee: float = 0.0
    
class OrderSchema(BaseModel):
    store_id: int
    picking_id: int
    product_items: List[DummyProduct]

class ConfirmPickingSchema(BaseModel):
    store_id: int
    picking_id: int
    state: str
