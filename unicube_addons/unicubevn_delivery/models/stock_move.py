#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from odoo import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    product_value = fields.Float(string="Product Value")
    contact_address = fields.Char('address', related="partner_id.contact_address_complete")