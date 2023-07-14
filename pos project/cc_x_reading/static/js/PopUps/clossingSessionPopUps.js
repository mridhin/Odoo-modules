odoo.define('cc_x_reading.ClosePosPopup', function (require) {
    'use strict';

    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');

    const PosBlackboxBeClosePopup = (ClosePosPopup) =>
        class extends ClosePosPopup {
            
            //edit the function below since this overwrites the default function
            //and is missing some of the functionality of the original function
            async closeSession() {
                let response;
                    response = await this.rpc({
                    model: 'pos.session',
                    method: 'clossing_session_x_reading_report',
                    args: [this.env.pos.pos_session.id],
                    kwargs: {

                    }
                })
                window.location = response.url;
                // return false;
                return super.closeSession();
            }
        };

    Registries.Component.extend(ClosePosPopup, PosBlackboxBeClosePopup);

    return ClosePosPopup;
});