# -*- coding: utf-8 -*-
import logging
import pprint
import threading
import time

from odoo import http, api, SUPERUSER_ID, registry
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.unicubevn_ipn.controllers.main import UniCubeBankController
from odoo.exceptions import AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


class UnicubeCheckout(UniCubeBankController):
    _process_url = '/payment/unicube/process'

    @http.route(_process_url, type='http', auth='public', csrf=False)
    def custom_process_transaction(self, **post):
        _logger.info("Handling custom processing with data:\n%s", pprint.pformat(post))
        _logger.info(request.env.uid)
        _logger.info(request.env.cr.dbname)
        # tx =  request.env['payment.transaction'].sudo()._handle_notification_data('unicube', post)

        # _logger.info(tx)
        threaded_calculation = threading.Thread(
            target=self.handle_notification_data, args=('unicube', post, request.env.cr.dbname))
        threaded_calculation.start()
        return request.redirect('/payment/status')

    def handle_notification_data(self, provider, post, db):
        # time.sleep(1)
        # _logger.info('provider', provider)
        # _logger.info('post', post)
        with registry(db).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            env['payment.transaction'].sudo()._handle_notification_data(provider, post)



    def website_invoice_handling(self, provider, data, txn_code, hash_id, payment_obj):
        """
        This function is handling the invoice payment for ecommerce purchase. For better UX, we use multi threading,
        :param provider: Payment provider code
        :param data: data to process
        :param txn_code: transaction code
        :param hash_id: hash ID of transaction
        :param payment_obj: payment object
        """
        if provider in ["timo", "atom"] and txn_code == "W":
            # Step 1: tx = self._get_tx_from_notification_data(provider_code, notification_data)
            # Step 3: tx._process_notification_data(notification_data)
            # Step 3: tx._execute_callback()
            # return tx
            _logger.info(
                f"Step 1: Website_invoice_handling for txn no with txn_code/hash_id: {txn_code}/{hash_id} is running...")
            # For threading, we need thread safe with right database cursor, so we take the 'dbname' from current
            # enviroment "request.env.cr.dbname". Then send the 'dbname' to new thread for further calculation
            threaded_calculation = threading.Thread(
                target=self.handle_notification_data, args=('unicube', data, request.env.cr.dbname))
            threaded_calculation.start()
            return request.redirect('/payment/status')
        return super(UnicubeCheckout, self).website_invoice_handling(provider, data, txn_code, hash_id, payment_obj)




class WebsiteSale(WebsiteSale):
    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.provider. State at this point :
         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.provider website but closed the tab without
           paying / canceling
        """
        order = request.website.sale_get_order()

        if order and (request.httprequest.method == 'POST' or not order.carrier_id):
            # Update order's carrier_id (will be the one of the partner if not defined)
            # If a carrier_id is (re)defined, redirect to "/shop/payment" (GET method to avoid infinite loop)
            carrier_id = post.get('carrier_id')
            keep_carrier = post.get('keep_carrier', False)
            if keep_carrier:
                keep_carrier = bool(int(keep_carrier))
            if carrier_id:
                carrier_id = int(carrier_id)
            order._check_carrier_quotation(force_carrier_id=carrier_id, keep_carrier=keep_carrier)
            if carrier_id:
                return request.redirect("/shop/payment")

        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('payment_methods_sudo', '')
            render_values.pop('tokens_sudo', '')
        _logger.info(f"render_values from shop_payment function: {render_values}")
        _logger.info(f"render_odoo: {render_values['providers_sudo']['company_id']['default_bank_acc']['acc_object']}")
        _logger.info(f"ref: {render_values['order']}")
        render_values['amount'] = int(render_values['amount'])
        _logger.info(f"amount: {render_values['amount']}")
        # TODO: should gen VIetQR here then send to frontend
        # Refactor to align with OCB rule
        render_values['acc_object'] = render_values['providers_sudo']['company_id']['default_bank_acc']['acc_object']
        return request.render("website_sale.payment", render_values)
