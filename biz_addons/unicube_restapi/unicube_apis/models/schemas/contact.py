from pydantic import BaseModel
from typing import List, Optional

class ContactSchema(BaseModel):
    name: str
    country_id: int | None = 241
    state_id: int
    mobile: str
    
    phone: str
    district_id: int
    ward_id: int
    # contact_address_complete: str

    street: str
    street2: str | None = None
    city: str | None = None

    store_id: int
    account_type: str | None = "2"
    company_id: int | None = 1
    active: bool | None = True
    