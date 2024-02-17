from odoo import models, fields, api

class Ward(models.Model):
    _name='res.country.ward'
    _description = 'ward'
    _order = 'name'

    #code;slug;slug2;name;district_code;district_name;city_code;city_name;district_id:id;state_id;country_id;type
    code = fields.Char(string="Ward Code")
    name = fields.Char("Ward name", translate=True)
    slug = fields.Char(string="Ward 3L",translate=True)
    slug2 = fields.Char(string="Ward 2L",translate=True)
    district_id = fields.Many2one('res.country.district', string='District',domain="[('state_id', '=', state_id)]")
    state_id = fields.Many2one(
        'res.country.state', 'State', domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', required=True, )
    type = fields.Selection(selection=[("0", "Phường"), ("1", "Xã"), ("2", "Thị trấn"), ("3", "Huyện")], string='Type')