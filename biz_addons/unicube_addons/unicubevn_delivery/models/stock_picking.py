#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
import logging
import uuid

from odoo import api, models, fields, Command
from collections import defaultdict
from datetime import date

# from unicube_restapi.unicube_apis.models.routers.handlerespon import make_response
from ..common.handlerespon import make_response

_logger = logging.getLogger(__name__)
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    """
        picking_type_id = 1 : Reciept
        picking_type_id = 2 : DO
    """

    # state_type_id = fields.Many2one(comodel_name='stock.picking.state_type', string='state_type_id')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    total_order = fields.Integer(string='Total Order')
    total_package_price = fields.Monetary(string='Package Price', currency_field='currency_id')
    total_price = fields.Monetary(string='Price', currency_field='currency_id')
    type = fields.Integer(string='Type', default=0)

    contact_phone = fields.Char(string='Phone')
    contact_address = fields.Char(string='Address')
    contact_name = fields.Char(string='Name')
    
    DO_id = fields.Integer(string='DO id')
    DO_state = fields.Char(string='Delivery Order State')

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        default=lambda self: self.env['res.currency'].search([('name', '=', 'VND')], limit=1),
        help='Currency for your monetary field'
    )
    qr_raw_data = fields.Char(string="QR data", compute="_compute_qr_data", store=True, default=False)
    qr_id = fields.Char("QR UUID", default=False)
    use_cod = fields.Boolean("Use COD", default=True)

    def action_tel(self):
        phone_number = self.contact_phone
        # Xây dựng URL để gọi điện thoại
        url = f'tel:{phone_number}'

        # Trả về action redirect đến URL
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',  # Mở URL trong cửa sổ hiện tại
        }

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.picking_type_id.id == 1:

            res_update = self.env['account.move'].sudo().search([('picking_id', '=', self._origin.id)]).write({
                'deliver_id': self.user_id.id
            })
        else:
            _picking_id = self.env['stock.picking'].sudo().search([('DO_id', '=', self._origin.id)])
            if not _picking_id:
                _logger.info('picking id not found!')
            else:
                self.env['account.move'].sudo().search([('picking_id', '=', _picking_id.id)]).write({
                    'receiver_id': self.user_id.id
                })
        pass

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

        if self.state == 'assigned' and self.picking_type_id.id == 1:
            _code = 5111
            try:
                _partner_id = self.partner_id.id
                if not _partner_id:
                    print('-----Cannot find Customer !----')
                    return False
                
                _type = self.type
                _name_ac_move = 'Delivery Pack (normal)' if _type == 0 else 'Delivery Pack (fast)'
                _total_price = self.total_price
                
                invoice_line_account_in_odoo = self.env['account.account'].search([('code','=',_code)])
                if not invoice_line_account_in_odoo:
                    print("Cannot find Account for the Invoice Line!")
                    return False

                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'invoice_origin': 'External API Demo',
                    'partner_id': _partner_id,
                    'ref': 'B65253',
                    'invoice_date': date.today(),
                    'invoice_date_due': date.today(),
                    'picking_id': self.id,
                    'deliver_id': self.user_id.id,
                    'receiver_id': self.user_id.id,
                    'invoice_line_ids': [(0,0,{
                        'name': _name_ac_move,
                        'account_id': invoice_line_account_in_odoo.id,
                        'price_unit': _total_price,
                        'quantity': 1
                    })],
                })

                if not invoice:
                    return make_response(msg='create account move failure!', status=1)
                return make_response(
                    msg='create invoice success ',
                )
            
            except Exception as e:
                print('----logg----', e)
        
        # elif self.state == 'draft' and self.picking_type_id.id == 2:
        #     self.env['stock.picking'].sudo().search([('DO_id','=', self.id)]).write({
        #         'DO_state': 'draft'
        #     })
        elif self.state == 'assigned' and self.picking_type_id.id == 2:
            self.env['stock.picking'].sudo().search([('DO_id','=', self.id)]).write({
                'DO_state': 'assigned'
            })
        elif self.state == 'done' and self.picking_type_id.id == 2:
            self.env['stock.picking'].sudo().search([('DO_id','=', self.id)]).write({
                'DO_state': 'done'
            })
        elif self.state == 'cancel' and self.picking_type_id.id == 2:
            self.env['stock.picking'].sudo().search([('DO_id','=', self.id)]).write({
                'DO_state': 'cancelled'
            })

        elif self.state == 'done' and self.picking_type_id.id == 1:
            print('logic create D.O here')
            new_picking = self.copy(
                default={
                        'picking_type_id': 2,
                        'partner_id': self.owner_id.id,
                        'company_id': 1,
                        'move_type': 'direct',
                        # 'total_order': self.total_order,
                        # 'total_package_price': self.total_package_price,
                        # 'total_price': self.total_price,
                        # 'type': self.type,
                        # 'contact_phone': self.contact_phone,
                        # 'contact_address': self.contact_address,
                        'use_cod': True,
                    }
                )
            print('-----new_picking----', new_picking)

            _stock_move = new_picking.move_ids[0]

            for move_line in self.move_line_ids:
                print("in loop",move_line)
                move_line.copy(default={
                    'move_id': new_picking.move_ids[0].id,
                    'picking_id': new_picking.id,
                    'quantity': 1,
                    'location_id': 8,
                })
            
            _stock_move.write({
                'location_id': 8,
                'location_dest_id': 4,

            })

            _update_picking = self.write({
                'DO_id': new_picking.id,
                'DO_state': new_picking.state
            })
            pass

        pass
