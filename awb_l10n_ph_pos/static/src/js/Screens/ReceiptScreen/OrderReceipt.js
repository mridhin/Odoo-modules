odoo.define('awb_l10n_ph_pos.OrderReceipt', function(require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    const OrderReceiptInherit = OrderReceipt =>
        class extends OrderReceipt{
            isSimple(line) {
                console.log("inherit activated");
                return (
                    line.discount === 0 &&
                    //if(isSimple()) will only display the name of the
                    //item and the price.
                    //added a condition that pricelist_discount must be 0
                    //to trigger isSimple(). this will trigger the format in OrderReceipt:
                    //<t t-if="isSimple(line)">
                    //else, it will display the pricelist discount if there are any.
                    line.pricelist_discount === 0 &&
                    line.is_in_unit &&
                    line.quantity === 1 &&
                    !(
                        line.display_discount_policy == 'without_discount' &&
                        line.price < line.price_lst
                    )
                );
            }
        }

    Registries.Component.extend(OrderReceipt,OrderReceiptInherit);

    return OrderReceipt;
});
