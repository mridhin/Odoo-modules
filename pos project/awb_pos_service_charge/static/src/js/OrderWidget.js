odoo.define('awb_pos_service_charge.OrderWidget', function (require) {
    'use strict';

    const { _t } = require('web.core');
    const { useState, useRef, onPatched } = owl.hooks;
    const OrderWidget = require('point_of_sale.OrderWidget');
    const Registries = require('point_of_sale.Registries');

    const ServiceOrderWidget = (OrderWidget) =>
        class extends OrderWidget {
        
        _updateSummary() {
	            const service_charge = this.order ? this.order.get_service_charge() : 0;
	            //this.state = useState({service_charge: 100});
	            this.state.service_charge = this.env.pos.format_currency(service_charge);
	            super._updateSummary();
        	}
        
        };

    Registries.Component.extend(OrderWidget, ServiceOrderWidget);

    return OrderWidget;
});
