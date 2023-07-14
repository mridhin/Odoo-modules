odoo.define('awb_pos_service_charge.ProductScreen', function(require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const POSserviceProductScreen = ProductScreen => class extends ProductScreen {
        
       async _updateSelectedOrderline(event) {
       		let { buffer } = event.detail;
       		let key = event.detail.key;
            let val = buffer === null ? 'remove' : buffer;
            let order = this.env.pos.get_order();
   			let selectedLine = order.get_selected_orderline();
   			var product = this.env.pos.db.get_product_by_id(this.env.pos.config.service_product_id[0]);
   			
   			if (selectedLine && selectedLine.get_product() == product) {
   			
   				if (val != 'remove' && key != "Backspace") {
            		//alert("Can not update service charge quantity or price, To update click on Service Button to change!");
            		
            		this.showPopup('ConfirmPopup', {
						title: this.env._t('Alert'),
						body: this.env._t('Please click on Service Charge Button to change service charge!!!'),
					});
            	}
   				
   			}
        	await super._updateSelectedOrderline(event);
        	var total_amount = this.env.pos.get_order().get_total_with_tax()
            this.env.pos.get_order()._update_service_amount()
        }
        
       async _newOrderlineSelected() {
            await super._newOrderlineSelected();
            this.env.pos.get_order()._update_service_amount()
        }
        
    };

    Registries.Component.extend(ProductScreen, POSserviceProductScreen);

    return ProductScreen;
});
