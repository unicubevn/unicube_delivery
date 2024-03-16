# -*- coding: utf-8 -*-
import json
import logging
import re
from datetime import datetime

from pyfcm import FCMNotification

from odoo import SUPERUSER_ID, _
from odoo.addons.unicubevn_bank.controllers.main import UniCubeBankController
from odoo.http import route, request, Response

_logger = logging.getLogger(__name__)


class UniCubeBankController(UniCubeBankController):
    _timo_ipn_url = "/cube/timo"
    _atom_ipn_url = "/cube/atom"
    _anchor = "CUB"

    def __init__(self):
        _timo_ipn_url = request.env['ir.config_parameter'].sudo().get_param('ipn.timo', "/cube/timo")
        _atom_ipn_url = request.env['ir.config_parameter'].sudo().get_param('ipn.atom', "/cube/atom")
        _anchor = request.env['ir.config_parameter'].sudo().get_param('ipn.anchor', "CUB")


    # ===== IPN URLs =====
    @route(_timo_ipn_url, auth="public", type="json", methods=["POST"],
           )
    def timo_ipn_handling(self, **kw):
        data = request.get_json_data()
        data.pop('apikey', None)  # remove apiKey
        _logger.info(f"ipn_handling function processing with data (note: apiKey is excluded:\n {data}")
        _logger.info("Step 1: Save to log...")

        data_obj = {
            'name': 'timo',
            'data': json.dumps(data),
        }
        store_result = request.env['ipn.log'].sudo().create(data_obj)
        _logger.info(f"Store result {store_result}")

        # if provider:
        _logger.info("Step 2: IPN Handling - starting...")
        result = self.invoice_handling('timo', data)
        _logger.info(f"Step 3: IPN Handling - result: {result}")
        if result:
            if type(result) is not Response:
                store_result.write({'account_payment_id': result.id})
                return {"message": "Successful"}
            else:
                _logger.info(
                    f"status: {result.status} - content_type: {result.content_type} - response: {result.response}")
                return {'status': result.status,
                        'content_type': result.content_type,
                        'response': result.response}

        return {"message": "This provider is not supported"}

    @route(_atom_ipn_url, auth="public", type="json", methods=["POST"],
           csrf=True, cors="*")
    def atom_ipn_handling(self, **kw):
        data = request.get_json_data()
        _logger.info(f"ipn_handling function processing with data (note: apiKey is excluded:\n {data}")
        _logger.info("Step 1: Save to log...")

        data_obj = {
            'name': 'atom',
            'data': json.dumps(data),
        }
        store_result = request.env['ipn.log'].sudo().create(data_obj)
        _logger.info(f"Store result {store_result}")

        # if provider:
        _logger.info("Step 2: IPN Handling - starting...")
        result = self.invoice_handling('atom', data)
        _logger.info(f"Step 3: IPN Handling - result: {result}")
        if result:
            if type(result) is not Response:
                store_result.write({'account_payment_id': result.id})
                return {"message": "Successful"}
            else:
                _logger.info(
                    f"status: {result.status} - content_type: {result.content_type} - response: {result.response}")
                return {'status': result.status,
                        'content_type': result.content_type,
                        'response': result.response}

        return {"message": "ATOM provider is supported"}

    # ===== Utilities functions =====
    def _narrative_parse(self, narrative_data=False, anchor="CUB", offset=8):
        if narrative_data:
            anchor_len = len(anchor)
            anchor_index = str(narrative_data).index(anchor)
            trans_index = anchor_index + anchor_len
            return narrative_data[trans_index:trans_index + 1], narrative_data[
                                                                anchor_index:anchor_index + offset + anchor_len + 1]

    def _register_payment_for_not_found_invoice(self, data, payment_obj):
        _logger.info("Start create account.payment object without mapping with invoice")
        _logger.info(f"Payment_obj: {payment_obj}")
        # mapping the payment for public user
        payment_obj['partner_id'] = request.env.ref('base.public_user').id
        #Have to convert communication field to ref field to meet the requirement of account.payment model
        payment_obj['ref'] = payment_obj['communication']
        payment_obj.pop('communication', None)
        payment = request.env['account.payment'].sudo().create(payment_obj)
        # Don't post the payment for further mapping
        # env = request.env(user=SUPERUSER_ID, su=True)
        # groups = env.ref('unicubevn_ipn.unicube_notify_group')
        # for user in groups.users:
        #     env['bus.bus']._sendone(user, 'simple_notification', {
        #         'type': 'success',
        #         'message': _("You have payment"),
        #         'sticky': True,
        #     })
            # channel_id.message_post(
            #     body=f'Order has been placed: {payment_obj}',message_type='notification',subtype_xmlid="mail.mt_comment")

        return payment

    # ===== Handle the payment logic =====
    def invoice_handling(self, provider, data):
        """
        This method is used for handling the logic for payment information from banks.
        """
        _logger.info(f"Provider: {provider} ")
        _logger.info(f"Transaction data {data}")
        #  ===== Check for anchor =====
        anchor_found = self._anchor in str(data['narrative']).upper()
        hash_id = ""
        txn_code = ""
        if anchor_found:
            txn_code, hash_id = self._narrative_parse(data['narrative'])

        # ===== Handle TIMO's transaction
        if provider == "timo":
            self._timo_provider_handler(provider, data, txn_code, hash_id)
        if provider == "atom":
            self._atom_provider_handler(provider, data, txn_code, hash_id)
        return super(UniCubeBankController, self).invoice_handling(provider, data)

    # ===== payment handling by payment provider =====
    def _timo_provider_handler(self, provider, data, txn_code, hash_id):
        # ===== Hash_id handle =====
        _logger.info("Start TIMO transaction handling process !")
        _logger.info(f"invoice_handling : provider: {provider} - data: {data}")
        _logger.info(f"Txn code: {txn_code} - hash ID: {hash_id}")

        # ===== Make payment object for TIMO provider
        # ===== Check whether the payment is outbound/inbound
        payment_type = 'outbound' if '-' in data['amount'] else 'inbound'
        partner_type = 'supplier' if '-' in data['amount'] else 'customer'
        payment_obj = {
            'amount': re.sub("[^0-9]", "", data["amount"]),
            'payment_type': payment_type,
            'partner_type': partner_type,
            'communication': f"{data['txnID']}-{data['narrative']}"
        }

        # ===== Search Bank Account and Mapping =====
        # Company_bank is the company account
        # Counter_bank is the vendor or customer bank
        company_bank = request.env['res.partner.bank'].sudo().search(
            [('|'), ('acc_number', '=', data['bankAccount']), ('proxy_value', '=', data['bankAccount'])])
        _logger.info(data['frmAcc'].replace("/", ""))
        counter_bank = request.env['res.partner.bank'].sudo().search([('acc_number', '=', data['frmAcc'])])
        _logger.info(f"company_bank: {company_bank}  - counter_bank:{counter_bank}")
        if company_bank:
            if payment_obj['payment_type'] == 'inbound':
                payment_obj['partner_bank_id'] = company_bank.id
            else:
                payment_obj['counter_bank_id'] = company_bank.id
        if counter_bank:
            if payment_obj['payment_type'] == 'inbound':
                payment_obj['counter_bank_id'] = counter_bank.id
                payment_obj['partner_id'] = counter_bank.partner_id.id
            else:
                payment_obj['partner_bank_id'] = counter_bank.id

        self._invoice_handler(provider, data, txn_code, hash_id, payment_obj)

    def _atom_provider_handler(self, provider, data, txn_code, hash_id):
        """
            ATOM callapi data handler:
            data:{
                  "amount": "10000",
                  "ccy": "VND",
                  "txnType": 0,
                  "fromAccName": "NGUYEN HOANG ANH",
                  "fromAccNo": "6769969",
                  "fromBankCode": "",
                  "fromAccBankBIN": "",
                  "vaId": "ATO0114825462USP8",
                  "vaName": "Bean Bakery",
                  "toAccNo": "0038100009629007",
                  "toAccName": "NGUYEN HOANG ANH",
                  "toAccBankCode": "OCB",
                  "toAccBankBIN": "970448",
                  "narrative": "CUBI19AFC586 The Bean Family thanh toan",
                  "clientTransId": "FT2405824LCJ\\BNK",
                  "traceId": "",
                  "transactionDate": "14:47:00 27/02/2024",
                  "bankDate": "2024-02-27",
                  "timestamp": 1708991276.317276,
                  "provider": "atom"
              }
        """
        # ===== Hash_id handle =====
        _logger.info("Start ATOM transaction handling process !")
        _logger.info(f"invoice_handling : provider: {provider} - data: {data}")
        _logger.info(f"Txn code: {txn_code} - hash ID: {hash_id}")
        # ===== Make payment object for TIMO provider
        # ===== Check whether the payment is outbound/inbound
        payment_type = 'outbound' if 'txnType' in data or data['txnType'] == 1 else 'inbound'
        partner_type = 'supplier' if 'txnType' in data or data['txnType'] == 1 else 'customer'
        payment_obj = {
            'amount': re.sub("[^0-9]", "", data["amount"]),
            'payment_type': payment_type,
            'partner_type': partner_type,
            'communication': f"{data['clientTransId']}-{data['narrative']}"
        }

        # ===== Search Bank Account and Mapping =====
        # Company_bank is the company account
        # Counter_bank is the vendor or customer bank
        company_bank = request.env['res.partner.bank'].sudo().search(
            [('|'), ('acc_number', '=', data['toAccNo']), ('proxy_value', '=', data['vaId'])])
        _logger.info(data['fromAccNo'].replace("/", ""))
        counter_bank = request.env['res.partner.bank'].sudo().search([('acc_number', '=', data['fromAccNo'])])
        _logger.info(f"company_bank: {company_bank}  - counter_bank:{counter_bank}")
        if company_bank:
            if payment_obj['payment_type'] == 'inbound':
                payment_obj['partner_bank_id'] = company_bank.id
            else:
                payment_obj['counter_bank_id'] = company_bank.id
        if counter_bank:
            if payment_obj['payment_type'] == 'inbound':
                payment_obj['counter_bank_id'] = counter_bank.id
                payment_obj['partner_id'] = counter_bank.partner_id.id
            else:
                payment_obj['partner_bank_id'] = counter_bank.id
        self._invoice_handler(provider, data, txn_code, hash_id, payment_obj)

    def _invoice_handler(self, provider, data, txn_code, hash_id, payment_obj):
        # Handling for website and pos transaction
        if txn_code == "W":
            return self.website_invoice_handling(provider, data, txn_code, hash_id, payment_obj)
        if txn_code == "P":
            return self.pos_invoice_handling(provider, data, txn_code, hash_id, payment_obj)
        # payment_obj['ref'] = f"{data['txnID']}-{data['narrative']}"
        # ===== Search and handle Invoice =====
        found_invoice = request.env['account.move'].sudo().search([('qr_id', '=', hash_id)])
        _logger.info(f"{found_invoice} - {found_invoice['state']}")

        # ===== handling the transaction that not paid via bill, invoice vietQR =====
        if not found_invoice:
            payment_obj['state'] = 'draft'
            return self._register_payment_for_not_found_invoice(data, payment_obj)

        # ===== handling the transaction that paid via bill, invoice vietQR =====
        if found_invoice['state'] == 'draft':
            found_invoice.write({'invoice_date': datetime.today().strftime('%Y-%m-%d')})
            found_invoice.action_post()
            payment_obj['partner_id'] = found_invoice.partner_id.id

        # Create payment and map with invoice
        # Have to remove the 'counter_bank_id' because it's not exist in 'account.payment.register' model
        payment_obj.pop("counter_bank_id", None)
        # payment_obj['communication'] = f"{data['narrative']}"
        _logger.info("Start create account.payment object then mapping with invoice")
        _logger.info(f"Payment_obj: {payment_obj}")
        payment = (request.env['account.payment.register'].sudo()
                   .with_context(active_model='account.move', active_ids=[found_invoice.id])
                   .create(payment_obj))

        payment = payment._create_payments()
        _logger.info(f"payment result: {payment}")

        return payment

    # ===== base method for VietQR transaction on Website =====
    def website_invoice_handling(self, provider, data, txn_code, hash_id, payment_obj):
        return self._register_payment_for_not_found_invoice(data, payment_obj)

    # ===== base method for VietQR transaction on POS =====
    def pos_invoice_handling(self, provider, data, txn_code, hash_id, payment_obj):
        return self._register_payment_for_not_found_invoice(data, payment_obj)
