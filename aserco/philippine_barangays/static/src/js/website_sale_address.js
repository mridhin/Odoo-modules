odoo.define('website_sale_options.website_sale_address', function (require) {
'use strict';

    const core = require('web.core');
    var ajax = require('web.ajax');

    var _t = core._t;
    require('web.dom_ready');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.ModalExample = publicWidget.Widget.extend({
    selector: '.checkout_autoformat',
        xmlDependencies: [],
        disabledInEditableMode: false,
        events: {
         'change select[name="state_id"]': '_onChangeState_id',
         'change select[name="city_id"]': '_onChangeCity_id',
        },

        _onChangeState_id: function(ev){
           var $target = $(ev.currentTarget)
//               debugger;
           var state_id = document.getElementsByName('state_id')[0].value;
           if ($target.val()){
                this._rpc({
                route: "/shop/order/select_city",
                params: {
                    'state_id':state_id,
                },
                }).then(function (data) {
                    // populate city and display
                    var selectCity = $("select[name='city_id']");
                    var odoocity = $("input[name='city']");
                    if (selectCity.data('init')===0 || selectCity.find('option').length===1) {
                        if (data.city_ids.length || data.city_required) {
                            selectCity.html('');

                            $.each(data.city_ids, function(key, value) {
                                selectCity.append($("<option></option>")
                                    .attr("value", value[0])
                                    .text(value[1])
                                    );
                            });
//                            selectCity.parent('div').show();
                            selectCity.show();
                            odoocity.hide();
                        } else {
//                            selectCity.val('').parent('div').hide();
                            selectCity.val('').hide();
                            odoocity.show();
                        }
                        selectCity.data('init', 0);
                    } else {
                        selectCity.data('init', 0);
                    }
                });
           }
        },

        _onChangeCity_id: function(ev){

            var $target = $(ev.currentTarget)
            console.log("call 11111111111111111111111111111");
            var city_id = document.getElementsByName('city_id')[0].value;
            console.log("222222222222222222222222",city_id)

           if ($target.val()){
                this._rpc({
                route: "/shop/order/select_barangay",
                params: {
                    'city_id':city_id,
                },
                }).then(function (data) {
                    console.log("barangay data",data);
                    // populate barangay and display
                    var selectBarangay = $("select[name='barangay_id']");
                    if (selectBarangay.data('init')===0 || selectBarangay.find('option').length===1) {
                        if (data.barangay_ids.length || data.barangay_required) {
                            selectBarangay.html('');

                            $.each(data.barangay_ids, function(key, value) {
                                selectBarangay.append($("<option></option>")
                                    .attr("value", value[0])
                                    .text(value[1])
                                    );
                            });
                            selectBarangay.parent('div').show();
                        } else {
                            selectBarangay.val('').parent('div').hide();
                        }
                        selectBarangay.data('init', 0);
                    } else {
                        selectBarangay.data('init', 0);
                    }
                });
           }
        }

    })
});