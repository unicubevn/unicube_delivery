#   Copyright (c) by The UniCube, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from odoo import models, fields
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env
from .routers.unicube_apis import router as unicube_api_router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("unicube_apis", "UniCube Api Endpoint")], ondelete={"unicube_apis": "cascade"}
    )
    def _get_fastapi_routers(self):
        if self.app == "unicube_apis":
            return [unicube_api_router]
        return super()._get_fastapi_routers()

