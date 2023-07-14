odoo.define('sh_pos_solo_parent_discount.models', function (require) {
    'use strict';

    const { Context } = owl;
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var field_utils = require('web.field_utils');

    var _super_Orderline = models.Orderline.prototype;
    var _super_Order = models.Order.prototype;

    models.Order = models.Order.extend({
        export_for_printing: function () {
            var super_export_for_printing = _super_Order.export_for_printing.bind(this)();

            var orderlines = [];
            var self = this;

            this.orderlines.each(function (orderline) {
                orderlines.push(orderline.export_for_printing());
            });

            var custom_total_discount = 0;

            var pricelist = this.pricelist;
            var string_limit = 15;
            var pricelist_name = pricelist.name;

            if (pricelist_name.length > string_limit) {
                pricelist_name = pricelist_name.slice(0, string_limit);
                pricelist_name = pricelist_name + '...';
            }

            for (var x = 0; x < orderlines.length; x++) {
                var regular_discount = 0;
                var discount_value = 0;

                custom_total_discount += Math.abs(discount_value) + +(orderlines[x].sc_discount_amount.toFixed(2)) + +(orderlines[x].pwd_discount_amount.toFixed(2))+ +(orderlines[x].sp_discount_amount.toFixed(2));
            }

            var to_return = _.extend(super_export_for_printing, {
                custom_total_discount: custom_total_discount,
            });
            return to_return;
        },
        recalculate_discount: function () {
            _super_Order.recalculate_discount.bind(this)();
            this.orderlines.each(function (line) {
                if (line.discount != 0) {
                    if (line.sp_discount != 0) {
                        var price_w_quantity = line.price * line.quantity;
                        var sp_discount_amount = price_w_quantity * line.sp_discount / 100;
                        line.sp_discount_amount = sp_discount_amount;
                    }
                }
                line.get_vat_info();
            });
        },
    });

    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            this.sp_discount = 0;
            this.sp_discount_amount = 0;
            this.is_sp_pressed = false;
            _super_Orderline.initialize.apply(this, arguments);
        },
        init_from_JSON: function (json) {
            this.sp_discount = json.sp_discount;
            this.sp_discount_amount = json.sp_discount_amount;
            this.is_sp_pressed = false;
            _super_Orderline.init_from_JSON.apply(this, arguments);
        },
        export_as_JSON: function () {
            var super_export_as_JSON = _super_Orderline.export_as_JSON.apply(this, arguments);

            super_export_as_JSON.sp_discount = this.sp_discount;
            super_export_as_JSON.sp_discount_amount = this.sp_discount_amount;

            return super_export_as_JSON;
        },
        export_for_printing: function () {
            var super_export_for_printing = _super_Orderline.export_for_printing.apply(this, arguments);
            super_export_for_printing.sp_discount = this.sp_discount;
            super_export_for_printing.sp_discount_amount = this.sp_discount_amount;
            super_export_for_printing.sp_discount_amount_Str = this.sp_discount_amount.toFixed(2);
            return super_export_for_printing;
        },
        reset_discounts: function () {
            this.sc_discount = 0;
            this.pwd_discount = 0;
            this.sp_discount = 0;
        },
    });
});