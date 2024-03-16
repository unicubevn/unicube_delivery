from odoo import api, fields, models, _
from odoo.exceptions import UserError

class DeliveryOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = "Unicubevn Sales Order Line"

    product_uom_qty = fields.Float(
        string="Quantity",
        compute='_compute_product_uom_qty',
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=True, required=True, precompute=True)
    