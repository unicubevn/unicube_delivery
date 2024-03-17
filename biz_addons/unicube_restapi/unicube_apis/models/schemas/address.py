from pydantic import BaseModel
from typing import List, Optional

class CountrySchema(BaseModel):
    country_id: int


class DistrictSchema(BaseModel):
    state_id: int

class WardSchema(BaseModel):
    district_id: int
