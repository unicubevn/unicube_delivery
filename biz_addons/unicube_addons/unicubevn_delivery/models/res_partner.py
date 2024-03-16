#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
from odoo import models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    store_id = fields.Many2one('res.partner', string='Store ID', required=True)
    account_type = fields.Selection([ ('1', 'Store'),('2', 'Customer'), ('3', 'Shiper')], string='Type', default='1')

    def action_create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """

        if len(self.user_ids) > 0:
            return {
                "type": "ir.actions.act_window",
                "res_model": "res.users",
                "views": [[False, "form"]],
                "res_id": self.user_ids[0].id,
                "target": "new",
            }

        if not self.mobile:
            print(self.env.user.partner_id)
            return self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'type': 'danger',
                'title': _("Warning"),
                'message': _('Must provide mobile number')
            })

        return self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email': self.email,
            'login': self.mobile.replace("+84", "0"),
            'password': "12345678",
            'partner_id': self.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
        })
