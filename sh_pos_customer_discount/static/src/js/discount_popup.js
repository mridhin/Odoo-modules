odoo.define('point_of_sale.DiscountPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    const { onMounted, useRef, useState } = owl;

    class DiscountPopup extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {string} props.startingValue
         */
        setup() {
            super.setup();
            this.state = useState({ inputValue: this.props.startingValue });
            this.inputRef = useRef('input');
        }
        async confirm() {
            debugger;
            const selectedOrderline = this.env.pos.get_order().get_selected_orderline();
            if (!selectedOrderline) return;

//            selectedOrderline.set_customer_note("With a Discount");
            selectedOrderline.set_discount(10);
        }
    }
    DiscountPopup.template = 'DiscountPopup';
    DiscountPopup.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: 'Discount',
        body: '',
    };

    Registries.Component.add(DiscountPopup);
    return DiscountPopup;
});

