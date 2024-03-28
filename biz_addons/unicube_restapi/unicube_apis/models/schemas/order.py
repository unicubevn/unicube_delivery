from pydantic import BaseModel
from typing import List, Optional

# class Items(BaseModel):
#     name: str | None = None

class Packages(BaseModel):
    package_price: float = 0.0
    desc: str | None = None
    price: float = 0.0
    
class OrderSchema(BaseModel):
    store_id: int
    contact_id: int
    picking_id: int
    type: int = 0
    package_items: List[Packages]

class ConfirmPickingSchema(BaseModel):
    store_id: int
    picking_id: int
    # state: str

