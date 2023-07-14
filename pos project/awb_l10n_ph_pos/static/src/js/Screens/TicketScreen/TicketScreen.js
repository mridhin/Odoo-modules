odoo.define('awb_l10n_ph_pos.TicketScreen', function (require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');

   /** Extend the TicketScreen widget */
   const PosOrderTicket = (TicketScreen) =>
     	class extends TicketScreen {
	        // @Override
		    constructor() {
		         super(...arguments);
		    }
     		 /** override the function to disable pay button */
		    getHasItemsToRefund() {
		            const order = this.getSelectedSyncedOrder();
		            if (!order) return false;
		            if (this._doesOrderHaveSoleItem(order)){
		            	/* Enable payment button when has item to refund */
		            	if ($('.pay')[0]) {
				        	$('.pay')[0].disabled = false;
			        	}
		            	return true;
		            }
		            	
		            const total = Object.values(this.env.pos.toRefundLines)
		                .filter(
		                    (toRefundDetail) =>
		                        toRefundDetail.orderline.orderUid === order.uid && !toRefundDetail.destinationOrderUid
		                )
		                .map((toRefundDetail) => toRefundDetail.qty)
		                .reduce((acc, val) => acc + val, 0);
		            
		            /* Enable payment button when has item to refund */
		            if (!this.env.pos.isProductQtyZero(total)) {
			            if ($('.pay')[0]) {
			        		console.log('ttttttt highlight')
				        	$('.pay')[0].disabled = false;
			        	}
			            return !this.env.pos.isProductQtyZero(total);
		            }
		            return !this.env.pos.isProductQtyZero(total);
		    }
    }
    Registries.Component.extend(TicketScreen, PosOrderTicket);
    return PosOrderTicket;
 });