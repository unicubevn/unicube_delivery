#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from odoo import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    product_value = fields.Float(string="Product Value")
    contact_address = fields.Char('address', related="partner_id.contact_address_complete")
    total_package_price = fields.Monetary(string='Package Price', currency_field='currency_id')
    total_price = fields.Monetary(string='Price', currency_field='currency_id')

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')], limit=1),
        help='Currency for your monetary field'
    )
    