odoo.define('sh_pos_customer_discount.DiscountButton', function (require) {
    'use strict';
   const { Gui } = require('point_of_sale.Gui');
   const PosComponent = require('point_of_sale.PosComponent');
   const { identifyError } = require('point_of_sale.utils');
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { useListener } = require("@web/core/utils/hooks");
   const Registries = require('point_of_sale.Registries');
   const PaymentScreen = require('point_of_sale.PaymentScreen');
   class DiscountButton extends PosComponent {

        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        async onClick() {
            let { confirmed, payload: discount } = await this.showPopup('TextInputPopup', {
                title: this.env._t('Discount'),
                startingValue: '',
                placeholder: this.env._t('Enter Discount Percentage'),
            });
            if (confirmed) {
                discount = Number(discount);
                if (discount !== '' && typeof discount === 'number' && discount > 0) {
                    var order  = this.env.pos.get_order()
                    const selectedOrderline = this.env.pos.get_order().get_selected_orderline();
//                    selectedOrderline.set_customer_note(discount_string);
                    selectedOrderline.set_discount(discount);
                }
            }
        }

//        constructor() {
//        super(...arguments);
//        }

//        display_discount_popup() {
//            var core = require('web.core');
//            var _t = core._t;
//            Gui.showPopup("DiscountPopup", {
//            title : _t("Discount"),
//            confirmText: _t("Exit")
//            });
//        }
   }

   DiscountButton.template = 'DiscountButton';
   ProductScreen.addControlButton({
       component: DiscountButton,
       condition: function() {
           return this.env.pos;
       },
   });
   Registries.Component.add(DiscountButton);
   return DiscountButton;
});