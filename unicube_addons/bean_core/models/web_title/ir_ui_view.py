# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class View(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def _render_template(self, template, values=None):
        if template in ['web.login', 'web.webclient_bootstrap', 'web.layout', 'web.report_preview_layout',
                        'web.report_layout', 'web.webclient_offline', 'mail.discuss_public_channel_template',]:
            if not values:
                values = {}
            values["title"] = self.env['ir.config_parameter'].sudo().get_param("web.base.title", "Bean")
            if "session_info" in values:
                values["session_info"]["support_url"] = self.env['ir.config_parameter'].sudo().get_param("web.support_url", "https://thebeanfamily.org")

            print(f"Bean core values - add title: {values}")

        return super(View, self)._render_template(template, values)
