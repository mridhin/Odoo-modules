odoo.define('awb_pos_sc_pwdID.ProductScreen', function(require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const POSpwdidProductScreen = ProductScreen => class extends ProductScreen {
       
        
        async _onClickCustomer() {
        	
        	const { confirmed, payload: pwd_id } = await this.showPopup('SCpwdPopup', {
                title: this.env._t('Enter SC/PWD ID'),
                startingValue: '',
            });

            let order = this.env.pos.get_order();
            order.setSCPWDID(pwd_id)
        	await super._onClickCustomer();
        }
    };

    Registries.Component.extend(ProductScreen, POSpwdidProductScreen);

    return ProductScreen;
});
