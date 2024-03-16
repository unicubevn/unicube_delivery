#   Copyright (c) by The UniCube, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class AuthJwtValidator(models.Model):
    _inherit = "auth.jwt.validator"

    partner_id_strategy = fields.Selection(selection_add=[("username", "From username claim")])

    def _get_partner_id(self, payload):
        # override for additional strategies
        print("unicube patching the '_get_partner_id' is running ...")
        print(" self.partner_id_strategy:",  self.partner_id_strategy)
        if self.partner_id_strategy == "username":
            print("username path is running ...", payload)
            username = payload.get("username")
            if not username:
                _logger.debug("JWT payload does not have an username claim")
                return
            # partner = self.env["res.partner"].search([("email", "=", email)])
            print("username:", username)
            user = self.env["res.users"].search([("login", "=", username)])
            print("user:", user)
            if len(user) != 1:
                _logger.debug("%d users found for username %s", len(user), username)
                return
            print("partner:", user.partner_id, " id: ",user.partner_id.id)
            print("partner name:", user.partner_id.name)
            return user.partner_id.id
        print("not username path is running ...")
        return super()._get_partner_id(payload)
