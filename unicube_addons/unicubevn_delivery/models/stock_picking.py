#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from odoo import api, models, fields
from collections import defaultdict

# from unicube_restapi.unicube_apis.models.routers.handlerespon import make_response
from ..common.handlerespon import make_response

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_id = fields.Many2one('account.move', string='Invoice')
    total_order = fields.Integer(string='Total Order')
    total_package_price = fields.Monetary(string='Package Price', currency_field='currency_id', digits=(16, 2))
    total_price = fields.Monetary(string='Price', currency_field='currency_id', digits=(16, 2))

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')], limit=1),
        help='Currency for your monetary field'
    )

    @api.depends('move_type', 'move_ids.state', 'move_ids.picking_id')
    def _compute_state(self):
        super()._compute_state()

        print('------logic here-----', self)
        if self.state == 'assigned':
            print('----logic create Invoice here-----')
        
            try:
                _partner = self.env['res.partner'].sudo().search([('id','=',self.partner_id)])
                if not _partner:
                    return make_response(msg='order dose not assiged')
                
                _result = self.env['account.move'].sudo().create({
                    'picking_id': self.id,
                    'company_id': self.company_id,
                    'partner_id': self.partner_id,
                    'partner_bank_id': 1,
                    'invoice_partner_display_name': _partner.name,

                })

                if not _result:
                    return make_response(msg='create account move failure!', status=1)
            except Exception as e:
                return make_response(msg=e, status=0)
            
        elif self.state == 'done':
            print('logic create D.O here')
        
        pass