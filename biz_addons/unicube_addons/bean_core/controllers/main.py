# -*- coding: utf-8 -*-
#   Copyright (c) by The Bean Family, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The Bean Family.


from odoo import http


class BeanController(http.Controller):

    @http.route('/website/info', type='http', auth="public")
    def bean_website_info(self, **kwargs):
        return "Hello, this page is maintained by UniCube"