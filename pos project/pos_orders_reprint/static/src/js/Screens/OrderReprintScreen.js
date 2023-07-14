odoo.define('pos_orders_reprint.OrderReprintScreen', function (require) {
	'use strict';

	const ReceiptScreen = require('point_of_sale.ReceiptScreen');
	const Registries = require('point_of_sale.Registries');

	const OrderReprintScreen = (ReceiptScreen) => {
		class OrderReprintScreen extends ReceiptScreen {
			constructor() {
				debugger;

				super(...arguments);
			}

			back() {
				debugger;
				this.props.resolve({ confirmed: true, payload: null });
				this.trigger('close-temp-screen');
			}
		}
		debugger;

		OrderReprintScreen.template = 'OrderReprintScreen';
		return OrderReprintScreen;
	};

	Registries.Component.addByExtending(OrderReprintScreen, ReceiptScreen);

	return OrderReprintScreen;
});
