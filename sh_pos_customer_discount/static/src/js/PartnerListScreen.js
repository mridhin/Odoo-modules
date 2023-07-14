odoo.define('sh_pos_customer_discount.PartnerListScreen', function(require) {
    'use strict';

    const PartnerListScreen = require('point_of_sale.PartnerListScreen');
    const Registries = require('point_of_sale.Registries');

    const PosLoyaltyPartnerListScreen = (PartnerListScreen) =>
        class extends PartnerListScreen {
                /**
                 * @override
                 */
            createPartner() {
            // initialize the edit screen with default details about country & state
                this.state.editModeProps.partner = {
                    country_id: this.env.pos.company.country_id,
                    state_id: this.env.pos.company.state_id,
                    sh_customer_discount: this.env.pos.company.sh_customer_discount,
                }
                this.activateEditMode();
            }
        };

    Registries.Component.extend(PartnerListScreen, PosLoyaltyPartnerListScreen);
    return PartnerListScreen;
});
