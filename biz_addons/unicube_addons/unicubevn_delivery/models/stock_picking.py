#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
import logging
import uuid

from odoo import api, models, fields
from collections import defaultdict

# from unicube_restapi.unicube_apis.models.routers.handlerespon import make_response
from ..common.handlerespon import make_response

_logger = logging.getLogger(__name__)
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_id = fields.Many2one('account.move', string='Invoice')
    total_order = fields.Integer(string='Total Order')
    total_package_price = fields.Monetary(string='Package Price', currency_field='currency_id')
    total_price = fields.Monetary(string='Price', currency_field='currency_id')
    type = fields.Integer(string='Type', default=0)

    contact_phone = fields.Char(string='Phone')
    contact_address = fields.Char(string='Address')

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')], limit=1),
        help='Currency for your monetary field'
    )
    qr_raw_data = fields.Char(string="QR data", compute="_compute_qr_data", store=True, default=False)
    qr_id = fields.Char("QR UUID", default=False)
    use_cod = fields.Boolean("Use COD")

    @api.depends('partner_id', 'total_package_price', 'name','use_cod')
    def _compute_qr_data(self, anchor="CUB", txn_code="D"):
        try:
            for record in self:
                print(record.company_id.country_id.code)
                if record.company_id.country_id.code == "VN":
                    # if not self.qr_id:
                    pay_content = f"{str(record.name).replace('/', '')}"
                    record.qr_id = f"{anchor}{txn_code}{str(uuid.uuid1())[:8]}".upper()
                    # record.qr_code_method = 'emv_qr'

                    if record.use_cod:
                        pay_content = f"Pay COD for receipt {pay_content}"
                        print(record.company_id.default_bank_acc)
                        qr_data = record.company_id.default_bank_acc.get_qr_data('emv_qr', record.total_package_price,
                                                                                 record.currency_id, '', '',
                                                                                 f"{record.qr_id} {pay_content}")
                    else:
                        pay_content = f"Pay for receipt {pay_content}"
                        print(record.partner_id.bank_ids[0])
                        qr_data = record.partner_id.bank_ids[0].get_qr_data('emv_qr', record.total_package_price,
                                                                            record.currency_id, '', '',
                                                                            f"{record.qr_id} {pay_content}")

                    _logger.info(
                        f"structured_communication: {record.qr_id} { pay_content}")
                    # ===== Generate VietQR
                    _logger.info(qr_data)
                    self.qr_raw_data = qr_data
        except Exception as X:
            _logger.info(f"_compute_qr_data have error:\n {X}")

    @api.depends('move_type', 'move_ids.state', 'move_ids.picking_id')
    def _compute_state(self):
        super()._compute_state()

        print('------logic here-----', self)
        if self.state == 'assigned':
            print('----logic create Invoice here-----')
        
            try:
                _partner = self.env['res.partner'].sudo().search([('id','=',self.partner_id.id)])
                print('--------_partner---', _partner)
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
                print('----logg----', e)
            
        elif self.state == 'done':
            print('logic create D.O here')
        
        pass
