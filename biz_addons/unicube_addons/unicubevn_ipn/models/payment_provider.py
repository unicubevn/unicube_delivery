from werkzeug.urls import url_join

from odoo.addons.unicubevn_payment.controllers.main import UnicubeCheckout
from odoo import _, api, fields, models


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('unicube', "UniCube")], ondelete={'unicube': 'set default'}
    )
    custom_mode = fields.Selection(
        selection_add=[('unicube_emv_qr', "UniCube VietQR")]
    )

    bank_account_id = fields.Many2one('res.partner.bank',
                                      string="Bank Account",
                                      readonly=True,
                                      check_company=True,
                                      related="journal_id.bank_account_id", store=False)
    bank_account_name = fields.Char(string="Bank Account",related="journal_id.bank_account_id.acc_number", store=False)
    bank_id = fields.Many2one('res.bank', related='journal_id.bank_id', readonly=True, store=False)
    ipn_url = fields.Char('IPN Url', compute="_get_ipn")

    _sql_constraints = [(
        'custom_providers_setup',
        "CHECK(custom_mode IS NULL OR ((code = 'custom' or code = 'unicube') AND custom_mode IS NOT NULL))",
        "Only custom/unicube providers should have a custom mode."
    )]

    # === ULTILITIES METHODS ===#
    @api.model
    def _get_ipn(self):
        self.ipn_url = url_join(self.get_base_url(), UnicubeCheckout._ipn_url)

    def send_to_timo(self):
        self.env['bus.bus']._sendone(self.env.user.partner_id, "simple_notification",
                                     {'type': 'success',
                                      'title': _("Notification"),
                                      'message': _('Send register data to TIMO.')
                                      })
    # === COMPUTE METHODS ===#

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'unicube').update(
            {'support_express_checkout': False,
             'support_manual_capture': 'partial',
             'support_refund': 'partial',
             'support_tokenization': False,
             })

    @api.depends('code')
    def _compute_view_configuration_fields(self):
        """ Override of payment to hide the credentials page.

        :return: None
        """
        super()._compute_view_configuration_fields()
        self.filtered(lambda p: p.code == 'unicube').update({
            'show_credentials_page': False,
            'show_pre_msg': True,
            'show_done_msg': True,
            'show_cancel_msg': True,
        })

    @api.model_create_multi
    def create(self, values_list):
        providers = super().create(values_list)
        providers.filtered(lambda p: p.custom_mode == 'unicube_emv_qr').pending_msg = None
        return providers



    def action_recompute_pending_msg(self):
        """ Recompute the pending message to include the existing bank accounts. """
        account_payment_module = self.env['ir.module.module']._get('account_payment')
        if account_payment_module.state == 'installed':
            for provider in self.filtered(lambda p: p.custom_mode == 'unicube_emv_qr'):
                company_id = provider.company_id.id
                accounts = self.env['account.journal'].search([
                    *self.env['account.journal']._check_company_domain(company_id),
                    ('type', '=', 'bank'),
                ]).bank_account_id
                account_names = "".join(f"<li><pre>{account.display_name}</pre></li>" for account in accounts)
                provider.pending_msg = f'<div>' \
                                       f'<h5>{_("Please use the following transfer details")}</h5>' \
                                       f'<p><br></p>' \
                                       f'<h6>{_("Bank Account") if len(accounts) == 1 else _("Bank Accounts")}</h6>' \
                                       f'<ul>{account_names}</ul>' \
                                       f'<p><br></p>' \
                                       f'</div>'

    def _get_removal_values(self):
        """ Override of `payment` to nullify the `custom_mode` field. """
        res = super()._get_removal_values()
        res['custom_mode'] = None
        return res

    def _transfer_ensure_pending_msg_is_set(self):
        transfer_providers_without_msg = self.filtered(
            lambda p: p.custom_mode == 'unicube_emv_qr' and not p.pending_msg
        )
        if transfer_providers_without_msg:
            transfer_providers_without_msg.action_recompute_pending_msg()
