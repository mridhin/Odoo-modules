odoo.define('sh_pos_solo_parent_discount.DiscountButtonSP', function (require) {
	'use strict';
	const { Gui } = require('point_of_sale.Gui');
	const PosComponent = require('point_of_sale.PosComponent');
	const { posbus } = require('point_of_sale.utils');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const { useListener } = require('web.custom_hooks');
	const Registries = require('point_of_sale.Registries');
	const PaymentScreen = require('point_of_sale.PaymentScreen');


	class DiscountButtonSP extends PosComponent {
		constructor() {
			super(...arguments);
			//useListener('click', this.onClick);
		}

		//Generate popup
		display_discount_popup_sp() {
			var core = require('web.core');
			var _t = core._t;

			var orderline = this.env.pos.get_order().get_orderlines();
			// console.log("SP button pressed", orderline);
			if (orderline.length != 0) {
				//to check if there is an orderline
				for (let line in orderline) {
					orderline[line].is_sp_pressed = true;
				}
			}

			Gui.showPopup("DiscountPopupSP", {
				title: _t("Discount"),
				confirmText: _t("Exit")
			});
		}

		is_available() {
			const order = this.env.pos.get_order();
			return order
		}
	}
	DiscountButtonSP.template = 'DiscountButtonSP';
	ProductScreen.addControlButton({
		component: DiscountButtonSP,
		condition: function () {
			return this.env.pos;
		},
	});

	Registries.Component.add(DiscountButtonSP);
	return DiscountButtonSP;
});