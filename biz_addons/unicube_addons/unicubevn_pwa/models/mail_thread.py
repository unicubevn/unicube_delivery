# -*- coding: utf-8 -*-

from pyfcm import FCMNotification
from odoo import models


class MailThread(models.AbstractModel):
    """Inherits MailThread to send notifications using chatterbox"""
    _inherit = 'mail.thread'

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        """Supering the _notify_thread() function to fetch the details of the
         chat message and push that message as a notification """
        res = super(MailThread, self)._notify_thread(message,
                                                     msg_vals=msg_vals,
                                                     **kwargs)
        msg = message.read()
        if self.env.company.push_notification and self.env.user.has_group(
                'base.group_user'):
            try:
                push_service = FCMNotification(
                    api_key=self.env.company.server_key)
                receiver_id = False
                domain = []
                if self.channel_type != 'channel':
                    for partner in self.channel_partner_ids:
                        if partner.id != msg[0]['author_id'][0]:
                            receiver_id = self.env['res.users'].search([(
                                'partner_id',
                                '=',
                                partner.id)])
                    if receiver_id:
                        domain = [('user_id', '=',
                                   receiver_id.id)]
                push_service.notify_multiple_devices(
                    registration_ids=[registration_id.register_id for
                                      registration_id in
                                      self.env['push.notification'].search(
                                          domain)],
                    message_title='Send by ' + msg[0]['author_id'][1],
                    message_body=msg[0]['description'],
                    extra_notification_kwargs={
                        'click_action': '/web'
                    })
            except Exception:
                pass
        return res
