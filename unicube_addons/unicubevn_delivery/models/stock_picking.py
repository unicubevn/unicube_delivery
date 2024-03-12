#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_id = fields.Many2one('account.move', string='Invoice')
    total_order = fields.Integer(string='Total Order')
    total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id', digits=(16, 2))
    total_fee = fields.Monetary(string='Total Fee', currency_field='currency_id', digits=(16, 2))

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')], limit=1),
        help='Currency for your monetary field'
    )
