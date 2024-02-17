# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'


    district_id = fields.Many2one(comodel_name='res.country.district', string='District',
                                  domain="[('state_id','=', state_id)]")
    ward_id = fields.Many2one(comodel_name='res.country.ward', string='Ward',
                              domain="[('district_id', '=', district_id)]")

    #Override the orginal '_prepare_display_address' function
    def _prepare_display_address(self, without_company=False):
        # get the information that will be injected into the display format
        # get the address format
        address_format = self._get_address_format()
        args = defaultdict(str, {
            # 'state_code': self.state_id.code or '',
            # 'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
        })
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format, args

    def _get_country_VN(self):
        self.country_id = 241


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

    @api.model
    def default_get(self, default_fields):
        """Set default value by fileds """
        values = super(Partner, self).default_get(default_fields)
        values.update({
            "country_id": 241,
        })
        return values
