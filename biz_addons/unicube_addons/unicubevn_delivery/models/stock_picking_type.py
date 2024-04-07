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
class StockPickingStateType(models.Model):
    _name = 'stock.picking.state_type'
    _description = 'abc'

    name = fields.Char(string='Name')
    state = fields.Char(string='state', helper="""('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),""")
    type = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        check_company=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)

    count_picking_draft = fields.Integer(compute='_compute_picking_count_shiper')
    count_picking_ready = fields.Integer(compute='_compute_picking_count_shiper')
    count_picking = fields.Integer(compute='_compute_picking_count_shiper')
    count_picking_waiting = fields.Integer(compute='_compute_picking_count_shiper')
    count_picking_late = fields.Integer(compute='_compute_picking_count_shiper')
    count_picking_backorders = fields.Integer(compute='_compute_picking_count_shiper')
    # ids = fields.One2many(comodel_name='stock.picking', string='ids', inverse_name='state_type_id', domain=[('state', '=')])

    def _get_action_shiper(self, action_xmlid):
        print('-----_get_action_shiper---click------')
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.display_name

        # context = {
        #     # 'search_default_picking_type_id': [self.id],
        #     'search_default_state': ['draft'],
        #     'default_picking_type_id': self.id,
        #     'default_state': self.state,
        #     'default_company_id': self.company_id.id,
        # }
        #
        # action_context = literal_eval(action['context'])
        # context = {**action_context, **context}
        # action['context'] = context
        print(f"[('state', '=', '{self.state}'),('picking_type_id', '=', {self.type.id})]")
        action['domain'] = [('state', '=', self.state),('picking_type_id', '=', self.type.id)]
        return action
    def get_stock_picking_action_picking_type_shiper(self):
        return self._get_action_shiper('stock.stock_picking_action_picking_type')


    def _compute_picking_count_shiper(self):
        domains = {
            'count_picking_draft': [('state', '=', 'draft')],
            'count_picking_waiting': [('state', 'in', ('confirmed', 'waiting'))],
            'count_picking_ready': [('state', '=', 'assigned')],
            'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_late': [('scheduled_date', '<', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_backorders': [('backorder_id', '!=', False), ('state', 'in', ('confirmed', 'assigned', 'waiting'))],
        }
        for field_name, domain in domains.items():
            data = self.env['stock.picking']._read_group(domain +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['__count'])
            count = {picking_type.id: count for picking_type, count in data}
            for record in self:
                record[field_name] = count.get(record.id, 0)
