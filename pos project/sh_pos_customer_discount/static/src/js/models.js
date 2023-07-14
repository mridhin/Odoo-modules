odoo.define('sh_pos_customer_discount.models', function (require) {
    'use strict';

    const { Context } = owl;
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var field_utils = require('web.field_utils');

    var _super_Orderline = models.Orderline.prototype;

    models.Orderline = models.Orderline.extend({
        get_price_with_tax_before_pricelist: function(){
            var default_pricelist = this.pos.default_pricelist;
            return this.product.get_display_price(default_pricelist, 1);
            
        },
        reset_discounts: function(){
            this.sc_discount = 0;
            this.pwd_discount = 0;
        },
        reset_unit_price: function(){
            console.log("reset_unit_price called");
            //this will trigger if there is an orderline.....
            if(this.pos.default_pricelist != this.order.pricelist){
                var temp_price_after_pricelist= this.product.get_price(this.order.pricelist, this.quantity, this.price_extra)
                this.set_unit_price(temp_price_after_pricelist);
            }
            else{
                this.set_unit_price(this.product.lst_price);
            }
        },
        //this is triggered everytime a user presses a number under
        //discount
        set_discount: function(discount){
            //reset the pwd/sc discounts when the manual discount is used.
            //this follows the functionality wherein only one discount between
            //sc, pwd, and regular discount will apply.
            this.reset_discounts();
            if(this.tax_ids != undefined){
                this.tax_ids = this.reset_taxes(this.tax_ids);
            }
            this.reset_unit_price();
            return _super_Orderline.set_discount.apply(this, arguments);
        },
        reset_taxes: function(tax_ids) {
            //accepts an array
            //resets the taxes of the orderline
            //if orderline.tax_ids != product.taxes_id
            //set orderline.tax_ids = product.taxes_id
            var product = this.product;
            
            if (!(_.isEqual(product.taxes_id.sort(), tax_ids.sort()))) {
                return product.taxes_id;
            }
        },
    });
});