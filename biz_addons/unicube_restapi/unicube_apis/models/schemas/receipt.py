from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, time, timedelta, date

class ReceiptSchema(BaseModel):
    store_id: int
    type: int # 0:normal or 1:fast
    scheduled_date: int

    contact_id: int
    contact_phone: str
    contact_address: str
