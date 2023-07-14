odoo.define('cc_z_reading.ClosePosPopup', function (require) {
    'use strict';

    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require('point_of_sale.Registries');

    const PosBlackboxBeClosePopup = (ClosePosPopup) =>
        class extends ClosePosPopup {
            
            //edit the function below since this overwrites the default function
            //and is missing some of the functionality of the original function
            async closeSession() {
                //trigger a function somehow if checkbox is checked9
                var is_end_of_day = document.getElementById('is_z_reading');
                console.log('is_end_of_day', is_end_of_day.checked);
                
                if(is_end_of_day.checked) {
                    let response;
                     response = await this.rpc({
                        model: 'pos.session',
                        method: 'clossing_session_report',
                        args: [this.env.pos.pos_session.id],
                        kwargs: {

                        }
                    })
                    window.location = response.url;
                }   
                return super.closeSession();
            }
        };

    Registries.Component.extend(ClosePosPopup, PosBlackboxBeClosePopup);

    return ClosePosPopup;
});