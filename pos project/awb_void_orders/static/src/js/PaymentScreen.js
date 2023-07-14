odoo.define('awb_void_orders.PaymentScreen', function(require) {
    'use strict';
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    
    const PaymentScreenInherit = PaymentScreen =>
        class extends PaymentScreen{
            async validateOrder(isForceValidate){
                // This is function is inherited from  PaymentScreen.
                // There might be a better way of inheriting this, but for now,
                // this is copy and pasted.

                // NOTE: Inheriting _finalizeValidation() might be better suited for 
                // voiding orders. For now, this works.

                if(this.env.pos.config.cash_rounding) {
                    if(!this.env.pos.get_order().check_paymentlines_rounding()) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Rounding error in payment lines'),
                            body: this.env._t("The amount of your payment lines must be rounded to validate the transaction."),
                        });
                        return;
                    }
                }
                if (await this._isOrderValid(isForceValidate)) {
                    // remove pending payments before finalizing the validation
                    for (let line of this.paymentLines) {
                        if (!line.is_done()) this.currentOrder.remove_paymentline(line);
                    }
                    
                    // NOTE: The following lines before calling _finalizeValidation()
                    //      is a custom code.
                    // For each orderline in the current order:
                    // check if refunded_orderline_id exists, 
                    // meaning that orderline is a refund,
                    // then call voidOrder function.

                    var payment_obj = this;
                    this.currentOrder.get_orderlines().forEach(function(orderline){
                        if(orderline.refunded_orderline_id){
                            payment_obj.voidOrder(orderline.refunded_orderline_id);
                        }
                    });

                    await this._finalizeValidation();
                }
            }

            async voidOrder(refunded_orderline_id) {
                // Calls voidOrderline method and passes the refunded_orderline_id
                // that is to be voided.
                let response;
                response = await this.rpc({
                    model: 'pos.order.line',
                    method: 'voidOrderline',
                    args: [refunded_orderline_id],
                    kwargs: {

                    }
                })
            }
        }

    Registries.Component.extend(PaymentScreen,PaymentScreenInherit);

    return PaymentScreen;
});