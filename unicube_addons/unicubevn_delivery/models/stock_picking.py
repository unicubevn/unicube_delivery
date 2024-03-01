#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_id = fields.Many2one('account.move', string='Invoice')
