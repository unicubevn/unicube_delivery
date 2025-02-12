/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";
import { EnterpriseNavBar } from "./navbar/navbar";

export class WebClientEnterprise extends WebClient {
    setup() {
        const title = document.title;
        super.setup();
        this.hm = useService("home_menu");
        this.title.setParts({ zopenerp: title });
    }
    _loadDefaultApp() {
        return this.hm.toggle(true);
    }
}
WebClientEnterprise.components = { ...WebClient.components, NavBar: EnterpriseNavBar };
