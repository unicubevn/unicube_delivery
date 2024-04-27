#   Copyright (c) by The UniCube, 2024.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
import logging
import uuid
import time

from odoo import api, models, fields, Command
from collections import defaultdict
from datetime import date
from ast import literal_eval
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_datetime, format_date, groupby

_logger = logging.getLogger(__name__)
class AccountMoveType(models.Model):
    _name = 'account.move.type'
    _description = 'account move for shiper'

    name = fields.Char(string='Name')
    type = fields.Char(string='Type')


    def get_account_action_type_shiper(self):
        print('-----get_account_action_type_shiper----', self)
        pass