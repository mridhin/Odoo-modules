odoo.define('awb_l10n_ph_pos.models', function (require) {
    'use strict';

    const { Context } = owl;
    var models = require('point_of_sale.models');
    var core = require('web.core');

    var _t = core._t;
    var _super_order = models.Order.prototype;

    var OrderlineCollection = Backbone.Collection.extend({
        model: _super_order.Orderline,
    });

    var PaymentlineCollection = Backbone.Collection.extend({
        model: _super_order.Paymentline,
    });


//     const PosModelInherit = PosModel =>
//        class extends PosModel{
//
//     push_single_order: function (order, opts) {
//        opts = opts || {};
//        const self = this;
//        const order_id = self.db.add_order(order.export_as_JSON());
//
//        return new Promise((resolve, reject) => {
//            self.flush_mutex.exec(async () => {
//                const order = self.db.get_order(order_id);
//                try {
//                    resolve(await self._flush_orders([order], opts));
//                } catch (error) {
//                    reject(error);
//                }
//            });
//        });
//    },
//
//    // saves the order locally and try to send it to the backend and make an invoice
//    // returns a promise that succeeds when the order has been posted and successfully generated
//    // an invoice. This method can fail in various ways:
//    // error-no-client: the order must have an associated partner_id. You can retry to make an invoice once
//    //     this error is solved
//    // error-transfer: there was a connection error during the transfer. You can retry to make the invoice once
//    //     the network connection is up
//
//    push_and_invoice_order: function (order) {
//        var self = this;
//        return new Promise((resolve, reject) => {
//            if (!order.get_client()) {
//                reject({ code: 400, message: 'Missing Customer', data: {} });
//            } else {
//                var order_id = self.db.add_order(order.export_as_JSON());
//                self.flush_mutex.exec(async () => {
//                    try {
//                        const server_ids = await self._flush_orders([self.db.get_order(order_id)], {
//                            timeout: 30000,
//                            to_invoice: true,
//                        });
//                        if (server_ids.length) {
//                            const [orderWithInvoice] = await self.rpc({
//                                method: 'read',
//                                model: 'pos.order',
//                                args: [server_ids, ['account_move']],
//                                kwargs: { load: false },
//                            });
//                            await self
//                                .do_action('account.account_invoices', {
//                                    additional_context: {
//                                        active_ids: [orderWithInvoice.account_move],
//                                    },
//                                })
//                                .catch(() => {
//                                    reject({ code: 401, message: 'Backend Invoice', data: { order: order } });
//                                });
//                        } else {
//                            reject({ code: 401, message: 'Backend Invoice', data: { order: order } });
//                        }
//                        resolve(server_ids);
//                    } catch (error) {
//                        reject(error);
//                    }
//                });
//            }
//        });
//    },
//
//    // wrapper around the _save_to_server that updates the synch status widget
//    // Resolves to the backend ids of the synced orders.
//    _flush_orders: function(orders, options) {
//        var self = this;
//        this.set_synch('connecting', orders.length);
//
//        return this._save_to_server(orders, options).then(function (server_ids) {
//            self.set_synch('connected');
//            for (let i = 0; i < server_ids.length; i++) {
//                self.validated_orders_name_server_id_map[server_ids[i].pos_reference] = server_ids[i].id;
//            }
//            return _.pluck(server_ids, 'id');
//        }).catch(function(error){
//            self.set_synch(self.get('failed') ? 'error' : 'disconnected');
//            throw error;
//        }).finally(function() {
//            self._after_flush_orders(orders);
//        });
//    },
//
//
//
//    }

    // load fields from res.company that was not previously loaded on the parent
    // class for getting the full address of the taxpayer

    models.load_fields('res.company', [
        'street',
        'street2',
        'city',
        'state_id',
        'zip',
    ]
    );

    // load fields from account.tax to get the tax_type of the product
    models.load_fields('account.tax', [
        'tax_type',
    ]);

    // extend the order class to alter the function mentioned below;
    // calculations for the vat/non-vat related info were added for the printing of the receipt;
    // later on, create a model to save the vat info in the database and
    // do the calculation in the python models;

    models.Order = models.Order.extend({
        // An order more or less represents the content of a client's shopping cart (the OrderLines)
        // plus the associated payment information (the Payment lines)
        // there is always an active ('selected') order in the Pos, a new one is created
        // automatically once an order is completed and sent to the server.

        export_for_printing: function () {

            var orderlines = [];
            var self = this;

            this.orderlines.each(function (orderline) {
                orderlines.push(orderline.export_for_printing());
            });

            // If order is locked (paid), the 'change' is saved as negative payment,
            // and is flagged with is_change = true. A receipt that is printed first
            // time doesn't show this negative payment so we filter it out.
            var paymentlines = this.paymentlines.models
                .filter(function (paymentline) {
                    return !paymentline.is_change;
                })
                .map(function (paymentline) {
                    return paymentline.export_for_printing();
                });
            var client = this.get('client');
            var cashier = this.pos.get_cashier();
            var company = this.pos.company;
            var date = new Date();

            function is_html(subreceipt) {
                return subreceipt ? (subreceipt.split('\n')[0].indexOf('<!DOCTYPE QWEB') >= 0) : false;
            }

            function render_html(subreceipt) {
                if (!is_html(subreceipt)) {
                    return subreceipt;
                } else {
                    subreceipt = subreceipt.split('\n').slice(1).join('\n');
                    var qweb = new QWeb2.Engine();
                    qweb.debug = config.isDebug();
                    qweb.default_dict = _.clone(QWeb.default_dict);
                    qweb.add_template('<templates><t t-name="subreceipt">' + subreceipt + '</t></templates>');

                    return qweb.render('subreceipt', { 'pos': self.pos, 'order': self, 'receipt': receipt });
                }
            }

            //the following are used for fetching the sales per receipt/invoice type
            //later have it be saved to the database
            var vatable_sales = 0;
            var vat_amount = 0;
            var zero_rated = 0;
            var vat_exempt = 0;
            var groupTaxes = [];
            var tax_details = this.get_tax_details();

            this.orderlines.each(function (line) {
                vatable_sales = 0;
                vat_amount = 0;
                zero_rated = 0;
                vat_exempt = 0;

                var taxDetails = line.get_tax_details();

                // 1. from groupTaxes, use the id and find the tax_type in tax_details
                // 2. if tax_type == etc. get price_without_tax as sales

                var taxIds = Object.keys(taxDetails);

                for (var t = 0; t < taxIds.length; t++) {
                    var taxId = taxIds[t];
                    groupTaxes.push(taxId);
                }

                for (var id = 0; id < groupTaxes.length; id++) {
                    for (var x in tax_details) {
                        if (groupTaxes[id] == tax_details[x].tax.id) {
                            var tax_type = tax_details[x].tax.tax_type;

                            if (tax_type == "zero_rated") {
                                zero_rated += orderlines[id].price_without_tax;
                            }
                            else if (tax_type == "vatable") {
                                vat_amount += orderlines[id].tax;
                                vatable_sales += orderlines[id].price_without_tax;
                            }
                            else if (tax_type == "vat_exempt") {
                                vat_exempt += orderlines[id].price_without_tax;
                            }
                        }
                    }
                }
            });

            var address_array = [company.city, company.state_id[1], company.zip];
            var address_info = "";
            for (var x = 0; x < address_array.length; x++) {
                if (address_array[x] != null) {
                    address_info = address_info + " " + address_array[x];
                }
            }

            var receipt = {
                receipt_number: this.pos.order.next_sequence_number, //display next receipt number
                zero_rated: zero_rated,
                vatable_sales: vatable_sales,
                vat_exempt: vat_exempt,
                vat_amount: vat_amount,
                orderlines: orderlines,
                paymentlines: paymentlines,
                subtotal: this.get_subtotal(),
                total_with_tax: this.get_total_with_tax(),
                total_rounded: this.get_total_with_tax() + this.get_rounding_applied(),
                total_without_tax: this.get_total_without_tax(),
                total_tax: this.get_total_tax(),
                total_paid: this.get_total_paid(),
                total_discount: this.get_total_discount(),
                rounding_applied: this.get_rounding_applied(),
                tax_details: this.get_tax_details(),
                change: this.locked ? this.amount_return : this.get_change(),
                name: this.get_name(),
                client: client ? client : null,
                invoice_id: null,   //TODO
                cashier: cashier ? cashier.name : null,
                precision: {
                    price: 2,
                    money: 2,
                    quantity: 3,
                },
                date: {
                    year: date.getFullYear(),
                    month: date.getMonth(),
                    date: date.getDate(),       // day of the month
                    day: date.getDay(),         // day of the week
                    hour: date.getHours(),
                    minute: date.getMinutes(),
                    isostring: date.toISOString(),
                    localestring: this.formatted_validation_date,
                    validation_date: this.validation_date,
                },
                company: {
                    email: company.email,
                    website: company.website,
                    company_registry: company.company_registry,
                    street: company.street,
                    street2: company.street2,
                    address_info: address_info,
                    city: company.city,
                    state: company.state_id[1],
                    zip: company.zip,
                    country: company.country_id[1],
                    vat: company.vat,
                    vat_label: company.country && company.country.vat_label || _t('Tax ID'),
                    name: company.name,
                    phone: company.phone,
                    logo: this.pos.company_logo_base64,
                },
                currency: this.pos.currency,
            };

            if (is_html(this.pos.config.receipt_header)) {
                receipt.header = '';
                receipt.header_html = render_html(this.pos.config.receipt_header);
            } else {
                receipt.header = this.pos.config.receipt_header || '';
            }

            if (is_html(this.pos.config.receipt_footer)) {
                receipt.footer = '';
                receipt.footer_html = render_html(this.pos.config.receipt_footer);
            } else {
                receipt.footer = this.pos.config.receipt_footer || '';
            }
            if (!receipt.date.localestring && (!this.state || this.state == 'draft')) {
                receipt.date.localestring = field_utils.format.datetime(moment(new Date()), {}, { timezone: false });
            }
            console.log(receipt);
            return receipt;
        }
    });
//    Registries.Component.extend(PosModel,PosModelInherit);
//    return PosModel;
});