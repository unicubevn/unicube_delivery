# -*- coding: utf-8 -*-
#   Copyright (c) by The Bean Family, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The Bean Family.

import odoo

# ----------------------------------------------------------
# Monkey patch release to set the edition as 'EE'
# ----------------------------------------------------------
odoo.release.version_info = odoo.release.version_info[:5] + ('e',)
if '+e' not in odoo.release.version:     # not already patched by packaging
    odoo.release.version = 'Bean Core {0}+e{1}{2} (based on Odoo CE) maintained by UniCube'.format(*odoo.release.version.partition('-'))

odoo.service.common.RPC_VERSION_1.update(
    server_version=odoo.release.version,
    server_version_info=odoo.release.version_info)
