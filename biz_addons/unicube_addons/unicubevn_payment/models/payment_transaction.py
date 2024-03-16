# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
import re
import uuid

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError

from odoo.addons.unicubevn_payment.controllers.main import UnicubeCheckout
from odoo.tools import image_data_uri

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    virtual_account = fields.Char(string="Virtual Account/Money Pot")
    # narrative = fields.Char(string="Narrative field")
    # use payment_id for virtual_account/bank account
    # use provider_reference for narrative
    vietqr = fields.Char(string="VietQR String", compute="_genVietQR", store=True)

    @api.depends("company_id", "amount", "reference")
    def _genVietQR(self, anchor="CUB", txn_code="W"):
        for record in self:
            _logger.info(record.provider_id.code)
            # The vietQr for payment.transaction still be created
            if record.provider_id.code == "unicube":
                # the bank will be the payment provider bank account, if not the company default bank account will be use
                bank = record.provider_id.bank_account_id if record.provider_id.bank_account_id else record.company_id.default_bank_acc
                hash_id = f"{anchor}{txn_code}{str(uuid.uuid1())[:8]}".upper()
                # generate 'narrative' content and translate
                communication = _(f"{hash_id} Pay invoice {record.reference}")
                record.virtual_account = bank.acc_number
                record.provider_reference = f"{record.provider_id.code}.{record.reference}.{hash_id}"
                # record.reference = communication
                record.callback_hash = hash_id
                _logger.info(
                    f"_genVietQR - data: record:{record} - callback_hash:{record.callback_hash} - content:{communication} - amount:{int(record.amount)}")
                record.vietqr = bank.get_qr(int(record.amount), content=communication)
                _logger.info(f"_genvietQR - result: callback_hash: {record.callback_hash} - vietqr: {record.vietqr} ")

    def gen_qr(self):
        # Force create vietQr string for each payment.transaction
        # TODO: need review: in case customer change the online order value, do we need to re-generate VietQR?
        if not self.vietqr:
            self._genVietQR()

        return image_data_uri(base64.b64encode(
            self.env['ir.actions.report'].barcode(barcode_type='QR', value=self.vietqr,
                                                  width=480, height=480, humanreadable=True)))

    def _narrative_parse(self, narrative_data=False, anchor="CUB", offset=8):
        if narrative_data:
            anchor_len = len(anchor)
            anchor_index = str(narrative_data).index(anchor)
            trans_index = anchor_index + anchor_len
            return narrative_data[trans_index:trans_index + 1], narrative_data[
                                                                anchor_index:anchor_index + offset + anchor_len + 1]

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return unicube-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'unicube':
            return res

        _logger.info(f"_get_specific_rendering_values : {self} - {self.callback_hash} - {self.reference}")

        res = {
            'api_url': UnicubeCheckout._process_url,
            'reference': self.reference,
            'vietqr': self.vietqr,
            'provider': self.provider_reference
        }
        # Don't know why system don't return transaction.callback_hash
        # So let do some workaround to get callback_hash value
        provider_ref_array = str(res['provider']).split(".")
        # provider_ref_array = str(self.provider_reference).split(".")
        res['hash_id'] = provider_ref_array[2]
        res['provider'] = provider_ref_array[0]
        _logger.info(f"_get_specific_rendering_values - res result:{self} - {res} ")
        return res
        # return {
        #     'api_url': UnicubeCheckout._process_url,
        #     'reference': self.reference,
        #     'hash_id': self.callback_hash,
        #     'vietqr': self.vietqr,
        #     'provider': "timo"
        # }


    def _get_post_processing_values(self):
        post_processing_values = super(PaymentTransaction, self)._get_post_processing_values()
        print("Provider code: %s", post_processing_values['provider_code'])
        if post_processing_values['provider_code'] == 'unicube':
            post_processing_values['vietqr'] = self.gen_qr()
        return post_processing_values

    # Step 1:
    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on unicube data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification feedback data
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        _logger.info(f"Step 1: Provider code: {provider_code} - notification data \n {notification_data}")
        if provider_code != 'unicube' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')

        if 'narrative' in notification_data:
            txn_code, callback_hash = self._narrative_parse(notification_data.get('narrative'))
        else:
            callback_hash = False
        _logger.info(
            f"Step 1 - _get_tx_from_notification_data: \n   reference: {reference} - callback_hash: {callback_hash}")
        _logger.info(f"notification_data: {notification_data}")
        # Find the transaction that match the callback_hash or (reference and payment provider code)
        if callback_hash:
            tx = self.search([('callback_hash', '=', callback_hash)])
        else:
            tx = self.search([('reference', '=', reference), ('provider_code', '=', 'unicube')])
        if not tx:
            raise ValidationError(
                "UniCube VietQR: " + _("No transaction found matching callback_hash %s.", callback_hash)
            )
        return tx

    # Step 2:
    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on unicube data.

        Note: self.ensure_one()

        :param dict notification_data: The unicube data
        :return: None
        """
        _logger.info(f"Step 2: notification data \n - Data: {notification_data}\n - Transaction no: {self}")

        if self.provider_code != 'unicube':
            return super()._process_notification_data(notification_data)

        _logger.info(
            f"validated UniCube payment for transaction {self} with: \n - reference {self.reference}\n - callback_hash {self.callback_hash}\n is set as 'pending'",
        )

        if 'amount' in notification_data:
            amount = float(
                re.sub("[^0-9]", "", notification_data['amount']))  # notification_data['amount'].replace(',', '')
            # amount = int(amount.replace('+', '') if '+' in amount else -amount.replace('-', ''))
            _logger.info(f"Amount: {amount} - {type(amount)} == Self Amount: {self.amount} - {type(self.amount)}")
            _logger.info(f"Is Amount the same?: {amount >= self.amount}")
            # TODO: Need to research the authorized flow
            if amount == self.amount:
                _logger.info("The transaction is fully paid.")
                self._set_done(state_message="Transaction is fully paid")
            else:
                message = "The transaction is over paid." if amount > self.amount else "The transaction is partial paid."
                _logger.info(message)
                self.amount = amount
                return self._set_done(state_message=message)
            # else:
            #     _logger.info("The transaction is partial paid.")
            #     return self._set_authorized(state_message="Transaction is partial paid")
        else:
            _logger.info("Waiting for IPN callback ...")
            self._set_pending()
        # must return True for continue handling...
        # return True

    def _log_received_message(self):
        """ Override of `payment` to remove unicube providers from the recordset.

        :return: None
        """
        other_provider_txs = self.filtered(lambda t: t.provider_code != 'unicube')
        super(PaymentTransaction, other_provider_txs)._log_received_message()

    def _get_sent_message(self):
        """ Override of payment to return a different message.

        :return: The 'transaction sent' message
        :rtype: str
        """
        message = super()._get_sent_message()
        if self.provider_code == 'unicube':
            message = _(
                "The customer has selected %(provider_name)s to make the payment.",
                provider_name=self.provider_id.name
            )
        return message

    def _set_pending(self, state_message=None, **kwargs):
        """ Override of `payment` to send the quotations automatically.

        :param str state_message: The reason for which the transaction is set in 'pending' state.
        :return: updated transactions.
        :rtype: `payment.transaction` recordset.
        """
        _logger.info("Setting pending is running...")
        txs_to_process = super()._set_pending(state_message=state_message, **kwargs)

        for tx in txs_to_process:  # Consider only transactions that are indeed set pending.
            _logger.info("txs_to_process is running...")
            sales_orders = tx.sale_order_ids.filtered(lambda so: so.state in ['draft', 'sent'])
            sales_orders.filtered(
                lambda so: so.state == 'draft'
            ).with_context(tracking_disable=True).action_quotation_sent()

            if tx.provider_id.code == 'unicube':
                _logger.info("UniCude do set_pending and compute SO ref")
                for so in tx.sale_order_ids:
                    _logger.info("sale_order_ids is running...")
                    so.reference = tx._compute_sale_order_reference(so)
            # send payment status mail.
            sales_orders._send_payment_succeeded_for_order_mail()
        _logger.info("Setting pending is ending...")
        return txs_to_process
