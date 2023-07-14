odoo.define('awb_l10n_ph_pos.ActionpadWidget', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const ActionpadWidget = require('point_of_sale.ActionpadWidget');
    
    /** Extend the ActionpadWidget */
    const Payment = (ActionpadWidget) =>
        class extends ActionpadWidget {
   	       // @Override
	        constructor() {
	            super(...arguments);
	            }
	        /** Get order line array and check order has a lines **/
	        get orderlinesArray() {
	        	var order = this.env.pos.get_order()
	        	var orderLine = order.get_orderlines() 
	        	var isOrder = false
	        	// check order line length
	        	if (orderLine.length === 0)
	        		isOrder = true
	        	console.log('has noOrderLine', isOrder)
	            return isOrder;
	        }
    }
    Registries.Component.extend(ActionpadWidget, Payment);
	return Payment;
});
    


