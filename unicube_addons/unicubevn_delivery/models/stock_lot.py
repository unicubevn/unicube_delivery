#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from odoo import models, fields, _


class StockLot(models.Model):
    _inherit = 'stock.lot'

    price = fields.Monetary(string='Price', currency_field='currency_id', digits=(16, 2))
    fee = fields.Monetary(string='Fee', currency_field='currency_id', digits=(16, 2))

    description = fields.Char(string='Description')
    address = fields.Char(string='Address')

    store_id = fields.Integer(string='Store Id')
    picking_id = fields.Integer(string='Receipt Id')
    delivery_order_id = fields.Integer(string='Delivery Order Id')

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')], limit=1),
        help='Currency for your monetary field'
    )
    type = fields.Integer(string='Type', default=0) # [ 0 is normal delivery , 1 is fast delivery ]
