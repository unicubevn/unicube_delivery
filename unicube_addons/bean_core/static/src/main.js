/** @odoo-module **/

import { startWebClient } from "@web/start";
import { WebClientEnterprise } from "./webclient/webclient";
import { registry } from "@web/core/registry";

/**
 * This file starts the enterprise webclient. In the manifest, it replaces
 * the community main.js to load a different webclient class
 * (WebClientEnterprise instead of WebClient)
 */
startWebClient(WebClientEnterprise);

// Remove some features in user_menuitems
var user_menu = registry.category("user_menuitems")
user_menu.remove("odoo_account")
user_menu.remove("documentation")
user_menu.remove("support")