odoo.define('awb_l10n_ph_pos.OrderRecieptPosProvider', function (require) {
    'use strict'
    const models = require('point_of_sale.models');
    models.load_fields('res.company',
        ['taxpayer_info',
            'taxpayer_is_vat_registered',
            'taxpayer_remarks',
            'company_display_address',
            'awb_pos_provider_id',
            'awb_pos_provider_tin',
            'awb_pos_provider_accreditation_no',
            'awb_pos_provider_display_date',
            'awb_pos_provider_display_valid_until',
            'awb_pos_provider_display_address',]);
    models.load_fields('res.partner',
        ['sc_pwd','check_sc_pwd','sc_id','pwd_id','bus_style','vat']);
    models.load_models([
        {
            //add domain to simplify the code in model.js
            model: 'crm.team',
            fields: [
                'taxpayer_min',
                'taxpayer_machine_serial_number',
                'awb_pos_provider_ptu',
                'awb_pos_provider_remarks',
                'current_sequence_number',
                'ending_sequence_number',
                'sale_team_prefix_id',
            ],
            domain: function(self){return [['id','=', self.config.crm_team_id[0]]];},
            loaded: function(self,data){
                self.team = data;
            }
        },
    ]);

        /*
            Removed since it is not used and its functionality is
                replicated in models.js.
        */
    
});