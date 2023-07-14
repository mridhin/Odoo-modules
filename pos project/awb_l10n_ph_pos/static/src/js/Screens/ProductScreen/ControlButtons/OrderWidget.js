odoo.define('awb_l10n_ph_pos.OrderWidget', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const OrderWidget = require('point_of_sale.OrderWidget');
    
    /** Extend the Order Widget */
    const Payment = (OrderWidget) =>
        class extends OrderWidget {
   	       // @Override
	        constructor() {
	            super(...arguments);
	        }
	        /** Disable payment button when there is no lines **/
	        get orderlinesArray() {
	        	var orderLine = this.order.get_orderlines() 
	        	if ($('.pay')[0]) {
	        		// if no lines disable payment button
		        	if (orderLine.length === 0){
		        		console.log('hasOrderLine', orderLine.length)
		        		$('.pay')[0].disabled = true;
		        	} else {
		        		$('.pay')[0].disabled = false;
		        	}
	        	}
	            return this.order ? this.order.get_orderlines() : [];
	        }
    }
    Registries.Component.extend(OrderWidget, Payment);
	return Payment;
});
    


