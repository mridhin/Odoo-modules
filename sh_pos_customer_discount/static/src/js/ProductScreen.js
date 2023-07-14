odoo.define('sh_pos_customer_discount.ProductScreen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    const PosCustomerDiscountProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async onClickPartner() {
                // IMPROVEMENT: This code snippet is very similar to selectPartner of PaymentScreen.
                const currentPartner = this.currentOrder.get_partner();
                if (currentPartner && this.currentOrder.getHasRefundLines()) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t("Can't change customer"),
                        body: _.str.sprintf(
                            this.env._t(
                                "This order already has refund lines for %s. We can't change the customer associated to it. Create a new order for the new customer."
                            ),
                            currentPartner.name
                        ),
                    });
                    return;
                }
                const { confirmed, payload: newPartner } = await this.showTempScreen(
                    'PartnerListScreen',
                    { partner: currentPartner }
                );
                if (confirmed) {
                    this.currentOrder.set_partner(newPartner);
                    this.currentOrder.updatePricelist(newPartner);
                    _.each(this.currentOrder.get_orderlines(), function (orderline) {
                        console.log("222222222222222222",orderline)
                        if (!orderline.discount) {
                            if (orderline && newPartner) {
                                orderline.set_discount(newPartner.sh_customer_discount)
                            }
                        } else {
                            if (newPartner && newPartner.sh_customer_discount == orderline.discount) {
                                if (newPartner) {
                                    orderline.set_discount(newPartner.sh_customer_discount)
                                } else {
                                    orderline.discount = 0
                                    orderline.discountStr = '' + 0
                                }
                            }
                        }
                    })
                }
            }
        };
    Registries.Component.extend(ProductScreen, PosCustomerDiscountProductScreen);
    return ProductScreen;
});
