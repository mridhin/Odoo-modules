odoo.define('pos_orders_list.PosOrdersDetail', function(require) {
	'use strict';

	const { useExternalListener } = owl.hooks;
	const PosComponent = require('point_of_sale.PosComponent');
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;

	class PosOrdersDetail extends AbstractAwaitablePopup {
		go_back_screen() {
			this.showScreen('ProductScreen');
			this.trigger('close-popup');
		}
		GetFormattedDate(date) {
		    var month = ("0" + (date.getMonth() + 1)).slice(-2);
		    var day  = ("0" + (date.getDate())).slice(-2);
		    var year = date.getFullYear();
		    var hour =  ("0" + (date.getHours())).slice(-2);
		    var min =  ("0" + (date.getMinutes())).slice(-2);
		    var seg = ("0" + (date.getSeconds())).slice(-2);
		    return year + "-" + month + "-" + day + " " + hour + ":" +  min + ":" + seg;
		}

		get_order_date(dt){
			dt +=' UTC' 
			let date = new Date(dt);
			let new_date = this.GetFormattedDate(date);
			return new_date
		}
	}
	
	PosOrdersDetail.template = 'PosOrdersDetail';
	Registries.Component.add(PosOrdersDetail);
	return PosOrdersDetail;
});
