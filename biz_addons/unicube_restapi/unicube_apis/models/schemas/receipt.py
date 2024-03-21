from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, time, timedelta, date

class ReceiptSchema(BaseModel):
    store_id: int
    type: int # 0:normal or 1:fast
    scheduled_date: int
    # scheduled_date: datetime
