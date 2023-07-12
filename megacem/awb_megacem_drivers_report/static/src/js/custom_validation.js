odoo.define("awb_megacem_drivers_report.CustomValidation", function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');

    /* Added the Method To genrate Restriction If Pondo After And Before Price is less than Zero also added restriction code for Hubreading fields*/
    var FormController = require('web.FormController');
    var ExtendFormController = FormController.include({
        _saveRecord: function () {
            if(this.modelName == 'drivers.report'){
                var record = this.model.get(this.handle, {raw: true});
                var stage_code = record["data"]["stage_code"]
                var pondo_before_trips = record["data"]['pondo_before_trips']
                var pondo_after_trips = record["data"]['pondo_after_trips']
                var hubreading_starting_location = record["data"]['hubreading_starting_location']
                var hubreading_plant_site = record["data"]['hubreading_plant_site']
                var hubreading_delivery_site = record["data"]['hubreading_delivery_site']
                var hubreading_ending_location = record["data"]['hubreading_ending_location']

                if(stage_code == 'approved') {
                    return this._super.apply(this, arguments);
                }

                self = this;

                if(stage_code != 'draft') {
                    /** Hubreading Tab **/
                    /** Fuel Details **/
                    if(pondo_before_trips <= 0){
                        self.do_warn(_t("Error: Pondo (Before Trips) value should not be equal to or less than zero (0)"));
                        return Promise.reject("SaveRecord: this.canBeSave is false");
                    }

                    if(pondo_after_trips <= 0){
                        self.do_warn(_t("Error: Pondo (After Trips) value should not be equal to or less than zero (0)"));
                        return Promise.reject("SaveRecord: this.canBeSave is false");
                    }
                }
                if (hubreading_starting_location || hubreading_plant_site || hubreading_delivery_site || hubreading_ending_location || stage_code != 'draft'){
                    if (hubreading_starting_location >= hubreading_plant_site){
                        self.do_warn(_t("Error: Hubreading Plant Site value should not be equal to or less than Hubreading Starting Location"));
                        return Promise.reject("SaveRecord: this.canBeSave is false");
                    }

                    if (hubreading_plant_site >= hubreading_delivery_site){
                        self.do_warn(_t("Error: Hubreading Delivery Site value should not be equal to or less than Hubreading Plant Site"));
                        return Promise.reject("SaveRecord: this.canBeSave is false");
                    }

                    if (hubreading_delivery_site >= hubreading_ending_location){
                        self.do_warn(_t("Error: Hubreading Ending Location value should not be equal to or less than Hubreading Delivery Site"));
                        return Promise.reject("SaveRecord: this.canBeSave is false");
                    }
                }

            }
        return this._super.apply(this, arguments);

        },
        
    });

});

