import requests

import clipboard

from odoo import models, fields, api


class TelegramChannel(models.Model):
    _name = 'telegram.channel'
    _description = 'Telegram Channel'

    name = fields.Char(string='Name', required=True)
    bot_name = fields.Char(string='Bot Name', help="Create your bot from Bot Father form Telegram App", required=True, )
    python_code = fields.Char(compute="_calc_python_code")
    chatID = fields.Char(string='Chat ID', required=True, help="Create yor channel , Add members , Add Bot As an Admin")

    test_message = fields.Char(string='Test Message', required=False, default='Test')

    def send_to_telegram(self, message):
        # if self.env.all.registry.db_name == 'odoo016':return

        message = self.env.all.registry.db_name + " : " + message
        apiURL = f'https://api.telegram.org/bot{self.bot_name}/sendMessage'
        try:
            requests.post(apiURL, json={'chat_id': self.chatID, 'text': message, 'parse_mode': 'html'})
        except Exception as e:
            print(e)

    def test_send(self):
        try:
            self.env.cr.savepoint()

            self.env['telegram.channel'].search([('name', '=', self.name)])[0].send_to_telegram(self.test_message)
        except Exception as e:
            print(e)

    @api.depends('name', 'chatID', 'bot_name')
    def _calc_python_code(self):
        print(self)
        for record in self:
            print(record)
            if not record.name:
                record.python_code = "please put a name"
            elif not record.test_message:
                record.test_message = "test"
                record.python_code = "please put a name"
            else:
                record.python_code = "self.env['telegram.channel'].search([('name', '=', '" + record.name + "')])[0].send_to_telegram('" + record.test_message + "')"

    def copy_chat_id(self):
        record = self.browse(self.id)
        clipboard.copy(record.python_code)

    def paste_chat_id(self):
        record = self.browse(self.id)
        chat_id = clipboard.paste()
        record.write({'chatID': chat_id})

    def paste_bot_name(self):
        record = self.browse(self.id)
        bot_name = clipboard.paste()
        record.write({'bot_name': bot_name})
