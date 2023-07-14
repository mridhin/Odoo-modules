odoo.define('awb_pos_coupon.pos', function (require) {
    'use strict';

    const models = require('point_of_sale.models');
    const rpc = require('web.rpc');
    const session = require('web.session');
    const concurrency = require('web.concurrency');
    const { Gui } = require('point_of_sale.Gui');
    const { float_is_zero,round_decimals } = require('web.utils');


    const dp = new concurrency.DropPrevious();

    class CouponCode {
        /**
         * @param {string} code coupon code
         * @param {number} coupon_id id of coupon.coupon
         * @param {numnber} program_id id of coupon.program
         */
        constructor(code, coupon_id, program_id) {
            this.code = code;
            this.coupon_id = coupon_id;
            this.program_id = program_id;
        }
    }

    var _order_super = models.Order.prototype;
    models.Order = models.Order.extend({
        // NEW METHODS
        activateCode: async function (code) {
            const promoProgram = this.pos.promo_programs.find(
                (program) => program.promo_barcode == code || program.promo_code == code
            );
            if (promoProgram && this.activePromoProgramIds.includes(promoProgram.id)) {
                Gui.showNotification('That promo code program has already been activated.');
            } else if (promoProgram) {
                // TODO these two operations should be atomic
                this.activePromoProgramIds.push(promoProgram.id);
                this.trigger('update-rewards');
            } else if (code in this.bookedCouponCodes) {
                Gui.showNotification('That coupon code has already been scanned and activated.');
            } else {
                const programIdsWithScannedCoupon = Object.values(this.bookedCouponCodes).map(
                    (couponCode) => couponCode.program_id
                );
                const customer = this.get_client();
                const { successful, payload } = await rpc.query({
                    model: 'pos.config',
                    method: 'use_coupon_code',
                    args: [
                        [this.pos.config.id],
                        code,
                        this.creation_date,
                        customer ? customer.id : false,
                        programIdsWithScannedCoupon,
                        this.get_total_with_tax(),
                        this.get_total_without_tax()
                    ],
                    kwargs: { context: session.user_context },
                });
                if (successful) {
                    // TODO these two operations should be atomic
                    this.bookedCouponCodes[code] = new CouponCode(code, payload.coupon_id, payload.program_id);
                    this.trigger('update-rewards');
                } else {
                    Gui.showNotification(payload.error_message);
                }
            }
        },
    });
});