odoo.define('sh_pos_customer_discount.pos', function (require) {
    'use strict';

    const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit')
    const PartnerListScreen = require('point_of_sale.PartnerListScreen')
    const Registries = require("point_of_sale.Registries");
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;

    const ShPartnerDetailsEdit = (PartnerDetailsEdit) =>
        class extends PartnerDetailsEdit {
            constructor() {
                super(...arguments);
            }
            saveChanges() {
                if (this.env.pos.config.sh_enable_customer_discount) {
                    var discount = $('#sh_customer_discount').val();
                    let processedChanges = {};
                    for (let [key, value] of Object.entries(this.changes)) {
                        if (this.intFields.includes(key)) {
                            processedChanges[key] = parseInt(value) || false;
                        } else {
                            processedChanges[key] = value;
                        }
                    }
                    if (discount) {
                        processedChanges['sh_customer_discount'] = discount || 0
                    }
//                    if ((!this.props.partner.name && !processedChanges.name) ||
//                        processedChanges.name === '') {
//                        return this.showPopup('ErrorPopup', {
//                            title: _t('A Customer Name Is Required'),
//                        });
//                    }
                    processedChanges.id = this.props.partner.id || false;
                    this.trigger('save-changes', { processedChanges });
                }
                else {
                    super.saveChanges()
                }
            }

        }
    Registries.Component.extend(PartnerDetailsEdit, ShPartnerDetailsEdit)

    const ShPartnerListScreen = (PartnerListScreen) =>
        class extends PartnerListScreen {
            constructor() {
                super(...arguments);
            }
            confirm() {
                super.confirm()
                if (this.env.pos.config.sh_enable_customer_discount) {
                    var self = this
                    var old_client = this.env.pos.get_order().get_partner();
                    _.each(this.env.pos.get_order().get_orderlines(), function (orderline) {
                        if (!orderline.discount) {
                            if (orderline && self.state.selectedClient) {
                                orderline.set_discount(self.state.selectedClient.sh_customer_discount)
                            }
                        } else {
                            if (old_client && old_client.sh_customer_discount == orderline.discount) {
                                if (self.state.selectedClient) {
                                    orderline.set_discount(self.state.selectedClient.sh_customer_discount)
                                } else {
                                    orderline.discount = 0
                                    orderline.discountStr = '' + 0
                                }
                            }
                        }
                    })
                }
            }

        }
    Registries.Component.extend(PartnerListScreen, ShPartnerListScreen)

    var _super_order = models.Order.prototype;
//    models.Order = models.Order.extend({
//        initialize: function (attr, options) {
//            _super_order.initialize.call(this, attr, options);
//            this.apply_discount = options.pos.config.sh_enable_customer_discount
//        },
//        add_product: function (product, options) {
//            _super_order.add_product.call(this, product, options)
//            if (this.apply_discount) {
//                var client = this.get_client()
//                if (client) {
//                    this.get_selected_orderline().set_discount(client.sh_customer_discount)
//                }
//            }
//        },
//    })
});
