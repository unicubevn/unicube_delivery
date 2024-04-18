#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from odoo import models, fields, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    picking_id = fields.Integer(string='Receipt Id')
    deliver_id = fields.Integer(string='Deliver ID')
    receiver_id = fields.Integer(string='Receiver ID')
