odoo.define('pos_orders_reprint.POSOrdersScreen', function (require) {
	'use strict';

	const POSOrdersScreen = require('pos_orders_list.POSOrdersScreen');
	const Registries = require('point_of_sale.Registries');
	const {useState} = owl.hooks;
	const {useListener} = require('web.custom_hooks');

	const BiPOSOrdersScreen = (POSOrdersScreen) =>
		class extends POSOrdersScreen {
			constructor() {
				super(...arguments);
				useListener('click-reprint', this.clickReprint);
			}

			async clickReprint(event){
				let self = this;
				let order = event.detail;

				await self.rpc({
					model: 'pos.order',
					method: 'print_pos_receipt',
					args: [order.id],
				}).then(function(output) {
					let data = output;
					data['order'] = order;
					self.showTempScreen('OrderReprintScreen',data);
				});

			}
		}
		
	Registries.Component.extend(POSOrdersScreen, BiPOSOrdersScreen);

	return POSOrdersScreen;
});


