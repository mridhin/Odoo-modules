/** @odoo-module **/
import AbstractAwaitablePopup from 'point_of_sale.AbstractAwaitablePopup';
import Registries from 'point_of_sale.Registries';
import PosComponent from 'point_of_sale.PosComponent';
import ControlButtonsMixin from 'point_of_sale.ControlButtonsMixin';
import NumberBuffer from 'point_of_sale.NumberBuffer';
import { useListener } from 'web.custom_hooks';
import { onChangeOrder, useBarcodeReader } from 'point_of_sale.custom_hooks';
const { useState } = owl.hooks;
const ProductScreen = require('point_of_sale.ProductScreen');

class ServicechargePopup extends AbstractAwaitablePopup {
	constructor() {
		super(...arguments);
		this.state = useState({ serviceData: { is_service_percentage: true, service_amount: 0 } });
	}

	get currentOrder() {
		return this.env.pos.get_order();
	}

	captureVat(event) {
		if (event.target.value == 'service_percentage') {
			this.state.serviceData['is_service_percentage'] = true;
			$(".percentage_symbol").show();
		} else {
			this.state.serviceData['is_service_percentage'] = false;
			$(".percentage_symbol").hide();
		} 
	}

	async applyConfirm() {
		//this.env.pos.get_order().add_product(product, options);
		//this.env.pos.config.service_product_id[0]
		var product = this.env.pos.db.get_product_by_id(this.env.pos.config.service_product_id[0]);
		var lines = this.env.pos.get_order().get_orderlines();
		
		if (product) {
			var lines = lines.filter(e => e.get_product() == product);
            for (var i = 0; i < lines.length; i++) {
                    lines[i].order.orderlines.remove(lines[i]);
                }
            var service_charge = 0
            var total_amount = (this.env.pos.get_order().get_total_with_tax() + this.env.pos.get_order().get_rounding_applied())
            if (this.state.serviceData['is_service_percentage'] && this.state.serviceData['service_amount']) {
            	service_charge = (this.state.serviceData['service_amount'] / 100.0)*total_amount
            } else {
            	service_charge = this.state.serviceData['service_amount']
            }
            this.env.pos.get_order().add_product(product, {
              quantity: 1,
              price: service_charge,
              lst_price: service_charge,
              is_service_charge: true,
              extras: {price_manually_set: true},
            });
            var lines = this.env.pos.get_order().get_orderlines();
            var line = lines.filter(e => e.get_product() == product);
			if (line.length > 0) {
				line[0].is_service_charge = true;
				if (this.state.serviceData['is_service_percentage'] && this.state.serviceData['service_amount']) {
	            		line[0].is_service_percentage = this.state.serviceData['is_service_percentage']
	            		line[0].service_percentage = this.state.serviceData['service_amount']
	            	} else {
            
            			line[0].is_service_percentage = this.state.serviceData['is_service_percentage']
	            		line[0].service_amount = this.state.serviceData['service_amount']
            		}
            	}
           var set_line = lines.filter(e => e.get_product() != product);
           if (set_line.length > 0) {
           		set_line[0].order.select_orderline(set_line[0]);
           }
            return this.trigger('close-popup');
        } else {
        	//this.trigger('close-popup');
        	this.showPopup('ConfirmPopup', {
						title: this.env._t('Alert'),
						body: this.env._t('Please go back to the configuration of this POS and make sure that the Service charge Product is not blank.'),
					});
        }
		//return this.trigger('close-popup');
	}

	async confirm() {
	}
	captureChange(event) {
		this.state.serviceData['service_amount'] = event.target.value;
		/* if ($("#service_selection_id").val() == 'service_percentage') {
			this.state.serviceData['service_amount'] = true;
		} else {
			this.state.serviceData['service_amount'] = false;
		} */
	}
	}
	//Create products popup
	ServicechargePopup.template = 'ServicechargePopup';
	ServicechargePopup.defaultProps = {
		confirmText: 'Ok',
		cancelText: 'Cancel',
		title: 'Discount',
		body: '',
	};
Registries.Component.add(ServicechargePopup);
//   return ServicechargePopup;
export default ServicechargePopup;
