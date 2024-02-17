from lxml import etree

from odoo import models, api, fields
from odoo.tools.translate import _


class ResCompany(models.Model):
    _inherit = "res.company"

    global_name = fields.Char("Global Name")
    short_name = fields.Char("Short Name")

    district_id = fields.Many2one(comodel_name='res.country.district', string='District',
                                  domain="[('state_id','=', state_id)]")
    ward_id = fields.Many2one(comodel_name='res.country.ward', string='Ward',
                              domain="[('district_id', '=', district_id)]")

    def _makeaddress(self, ward_name="", district_name=""):
        if (ward_name != False and district_name != False):
            return (str(ward_name) + ", " + str(district_name))
        else:
            return ""

    @api.onchange('district_id')
    def _district_onchange(self):
        self.street2 = self.district_id.name
        self.ward_id = False
        self.city = self.state_id.name

    @api.onchange('ward_id')
    def _ward_onchange(self):
        self.street2 = self.ward_id.slug2
        self.city = self.state_id.name

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            self.city = self.state_id.name
            self.district_id = False
            self.ward_id = False
            # self.zip = self.state_id.zipcode
        elif self._origin:
            self.district_id = False
            self.ward_id = False
            self.city = False
            self.zip = False

    # @api.model
    # def _address_fields(self):
    #     """Returns the list of address fields that are synced from the parent."""
    #     return super(ResCompany, self)._address_fields() + ['state_id', ]


    @api.model
    def _default_get(self, default_fields):
        """Set default value by fields """
        values = super(ResCompany, self)._default_get(default_fields)
        values.update({
            "default_website": "https://",
            "default_country_id.id": 241,
        })
        return values
