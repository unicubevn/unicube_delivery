from odoo import models, fields


class District(models.Model):
    # _name is the important field to define the global name of model
    _name = "res.country.district"
    # _descriptin is define the friendly name for model
    _description = "District"
    _order = "code"

    name = fields.Char('District name', translate=True)
    code = fields.Char(string="District Code", help='The District code.', required=True)
    slug = fields.Char(string="District Slug")
    state_id = fields.Many2one(
        'res.country.state', 'State')
    country_id = fields.Many2one('res.country', string='Country', required=True, )
    type = fields.Selection(selection=[("0", "Quận"), ("1", "Huyện"), ("2", "Thị xã"), ("3", "Thành Phố")], string='Type')

    def get_website_sale_district(self, mode='billing'):
        return self.sudo().search([])
