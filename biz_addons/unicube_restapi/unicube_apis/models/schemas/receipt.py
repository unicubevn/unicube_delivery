from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, time, timedelta

class ReceiptSchema(BaseModel):
    store_id: int
    type: int # o:normal or 1:fast
    scheduled_date: datetime
