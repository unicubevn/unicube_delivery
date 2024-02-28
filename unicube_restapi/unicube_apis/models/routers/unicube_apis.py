#   Copyright (c) by The UniCube, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.

from typing import Annotated, Union

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.api import Environment

router = APIRouter()

class PartnerInfo(BaseModel):
    name: str
    email: str

class TestData(BaseModel):
    name: Union[str, None] = None
    email: Union[str, None] = None
    uid: int
@router.get("/partners", response_model=list[PartnerInfo])
def get_partners(env: Annotated[Environment, Depends(odoo_env)]) -> list[PartnerInfo]:
    return [
        PartnerInfo(name=str(partner.name), email=partner.email if partner.email else "No email" )
        for partner in env["res.partner"].sudo().search([])
    ]
