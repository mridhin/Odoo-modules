odoo.define('awb_l10n_ph_pos.models', function (require) {
    'use strict';

    const { Context } = owl;
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var field_utils = require('web.field_utils');

    var _t = core._t;
    var _super_order = models.Order.prototype;
    var _super_Orderline = models.Orderline.prototype;

    var OrderlineCollection = Backbone.Collection.extend({
        model: _super_order.Orderline,
    });

    var PaymentlineCollection = Backbone.Collection.extend({
        model: _super_order.Paymentline,
    });

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
    
    /*
        Created an increment tracker for the sequence number.
        This will increment at the start of every order.
        This does not affect the backend.
        This only displays the computed sequence number from this js
            and is trying to emulate the sequence number of the backend.
        This is trying to bypass the bug wherein the info fetched from the
            backend is not updating per order, hence the frozen sequence number.
        This is a temporary fix. There are probably better ways of solving
            this bug.
    */
    var increment = 0;

    // extend the order class to alter the function mentioned below;
    // calculations for the vat/non-vat related info were added for the printing of the receipt;
    // later on, create a model to save the vat info in the database and
    // do the calculation in the python models;
    models.Order = models.Order.extend({
        // An order more or less represents the content of a client's shopping cart (the OrderLines)
        // plus the associated payment information (the Paymentlines)
        // there is always an active ('selected') order in the Pos, a new one is created
        // automaticaly once an order is completed and sent to the server.
        initialize: function(attributes,options){
            console.log("initialize inherited");

            var self = this;
            options  = options || {};
            
            /*
                `increment` increments after every order.
            */
            increment++;
            this.locked         = false;
            this.pos            = options.pos;
            this.selected_orderline   = undefined;
            this.selected_paymentline = undefined;
            this.screen_data    = {};  // see Gui
            this.temporary      = options.temporary || false;
            this.creation_date  = new Date();
            this.to_invoice     = false;
            this.orderlines     = new OrderlineCollection();
            this.paymentlines   = new PaymentlineCollection();
            this.pos_session_id = this.pos.pos_session.id;
            this.employee       = this.pos.employee;
            this.finalized      = false; // if true, cannot be modified.
            this.set_pricelist(this.pos.default_pricelist);
    
            this.set({ client: null });
    
            this.uiState = {
                ReceiptScreen: new Context({
                    inputEmail: '',
                    // if null: not yet tried to send
                    // if false/true: tried sending email
                    emailSuccessful: null,
                    emailNotice: '',
                }),
                TipScreen: new Context({
                    inputTipAmount: '',
                })
            };
            
            /*
                The following are for initializing the first sequence number that will be incremented
                    as well as other sequence number information.
            */
            this.current_sequence_number = this.pos.team[0].current_sequence_number;
            this.ending_sequence_number = this.pos.team[0].ending_sequence_number;
            this.sale_team_prefix = this.pos.team[0].sale_team_prefix_id[1];
            this.final_sequence_number = "";

            /*
                This adds the increment to the current_sequence_number that stays frozen
                    even after multiple orders (maybe because it is always initializing,
                        therefore always having the same value.)
            */
            this.increment_sequence_number = this.current_sequence_number + increment;

            if (options.json) {
                this.init_from_JSON(options.json);
            } else {
                this.sequence_number = this.pos.pos_session.sequence_number++;
                this.uid  = this.generate_unique_id();
                this.name = _.str.sprintf(_t("Order %s"), this.uid);
                this.validation_date = undefined;
                this.fiscal_position = _.find(this.pos.fiscal_positions, function(fp) {
                    return fp.id === self.pos.config.default_fiscal_position_id[0];
                });
            }
    
            this.on('change',              function(){ this.save_to_db("order:change"); }, this);
            this.orderlines.on('change',   function(){ this.save_to_db("orderline:change"); }, this);
            this.orderlines.on('add',      function(){ this.save_to_db("orderline:add"); }, this);
            this.orderlines.on('remove',   function(){ this.save_to_db("orderline:remove"); }, this);
            this.paymentlines.on('change', function(){ this.save_to_db("paymentline:change"); }, this);
            this.paymentlines.on('add',    function(){ this.save_to_db("paymentline:add"); }, this);
            this.paymentlines.on('remove', function(){ this.save_to_db("paymentline:rem"); }, this);
    
            if (this.pos.config.iface_customer_facing_display) {
                this.paymentlines.on('add', this.pos.send_current_order_to_customer_facing_display, this.pos);
                this.paymentlines.on('remove', this.pos.send_current_order_to_customer_facing_display, this.pos);
            }
    
            this.save_to_db();
    
            return this;
        },
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

            var address_array = [company.city, company.state_id[1], company.zip];
            
            
            // match the crm_team_id of this session to this.pos.team.id
            // get the sales team's info 

            // var this_crm_team_id = this.pos.config.crm_team_id;
            // console.log("crm_team_id ", this_crm_team_id);

            // var all_sales_team = this.pos.team;
            // console.log("all sales team", all_sales_team);

            var min = "";
            var sn = "";
            var ptu = "";
            var remarks = "";
            
            min = this.pos.config.taxpayer_min;
            sn = this.pos.config.taxpayer_machine_serial_number;
            ptu = this.pos.config.awb_pos_provider_ptu;
            remarks = this.pos.team[0].awb_pos_provider_remarks;
            
            // VAT inclusive prices computations
            // variable initialization
            // remove unused variables later.
            
            // for getting the discounts from pricelist
            // Discount radio button should be configured
            // Get percentage -> discount
            // price = price - (price * (rule.percent_price / 100));
            // therefore discount = price * (pricelist.percent_price / 100);
            // access selected pricelist via this.pricelist
            // integrate per orderline
            // check if pricelist is triggered
            // get discounts

            var custom_total_discount = 0;

            // get pricelist info
            var pricelist = this.pricelist;
            var string_limit = 15;
            var pricelist_name = pricelist.name;
            console.log("pricelist > ", pricelist);
            console.log("default pricelist > ", this.pos.default_pricelist);
            
            if(pricelist_name.length > string_limit){
                pricelist_name = pricelist_name.slice(0, string_limit);
                pricelist_name = pricelist_name + '...';
            }

            var promo = this.activePromoProgramIds;
            // for every orderline
            for(var x = 0; x < orderlines.length; x++){
                //reset variables
                var fixed_lst_price_w_quantity = 0;

                var after_pricelist_discount_value = 0;
                var regular_discount = 0;
                var discount_value = 0;

                var pricelist_discount = 0;
                var pricelist_discount_value = 0;


                console.log("for orderlines", orderlines[x]);

                //fixed_lst_price_w_quantity = price_display by default
                //price_display contains tax and discount already.
                //promo not included in discount computation
                var tax_details = this.get_tax_details();
                if (!(orderlines[x].price_display < 0)){
                    fixed_lst_price_w_quantity = orderlines[x].price_with_tax_before_pricelist * orderlines[x].quantity;
                }

                //check if there is a promo
                if (promo){
                    if (orderlines[x].price_display < 0) {
                        discount_value = orderlines[x].price_display;
                    }
                }
                
                //save all computations to the orderlines object for fetching
                // Math.round(3.14159 * 100) / 100
                // use Math.round to return a number; use the formula above for 2 decimal places
                // toFixed returns a string which does not allow computations later on
                
                var parsed_discount = typeof(regular_discount) === 'number' ? regular_discount : isNaN(parseFloat(regular_discount)) ? 0 : field_utils.parse.float('' + regular_discount);
                var disc = Math.min(Math.max(parsed_discount || 0, 0),100);
                        
                orderlines[x].regular_discount = 0;
                orderlines[x].discount_value = 0; // discount

                orderlines[x].fixed_lst_price_w_quantity = Math.round(fixed_lst_price_w_quantity * 100) / 100;

                custom_total_discount += Math.abs(discount_value) + +(orderlines[x].sc_discount_amount.toFixed(2)) + +(orderlines[x].pwd_discount_amount.toFixed(2));
                console.log("custom_total_discount ", custom_total_discount);
                console.log("Math.round(orderlines[x].sc_discount_amount * 100) / 100 ", Math.round(orderlines[x].sc_discount_amount * 100) / 100);
                console.log("+(orderlines[x].sc_discount_amount.toFixed(2))", +(orderlines[x].sc_discount_amount.toFixed(2)));
                
            }   

            //the following are used for fetching the sales per receipt/invoice type
            //later have it be saved to the database
            var vatable_sales = 0;
            var senior_citizen_pwd_total_with_vat = 0;
            var senior_citizen_pwd_total_without_vat = 0;
            var senior_citizen_pwd_total = 0
            var senior_citizen_disc = 0;
            var pwd_citizen_disc = 0;
            var solo_parent_disc = 0;
            var vat_amount = 0;
            var zero_rated = 0;
            var vat_exempt = 0;
            var groupTaxes = [];
            var tax_details = this.get_tax_details();

            var default_pricelist = this.pos.default_pricelist;

            for(var x = 0; x < orderlines.length; x++){
                senior_citizen_pwd_total += orderlines[x].fixed_lst_price_w_quantity
                if (orderlines[x].is_vat_exclusive) {
                    senior_citizen_pwd_total_with_vat += orderlines[x].fixed_lst_price_w_quantity
                    senior_citizen_pwd_total_without_vat += orderlines[x].price_with_tax_before_discount
                    senior_citizen_disc += parseFloat(orderlines[x].sc_discount_amount.toFixed(2))
                    pwd_citizen_disc += parseFloat(orderlines[x].pwd_discount_amount.toFixed(2))
                    solo_parent_disc += parseFloat(orderlines[x].sp_discount_amount.toFixed(2))
                }
            }

            var senior_citizen_pwd_vat = (senior_citizen_pwd_total_with_vat - senior_citizen_pwd_total_without_vat).toFixed(2)
            var senior_citizen_pwd_without_vat = (senior_citizen_pwd_total - senior_citizen_pwd_vat).toFixed(2)

            this.orderlines.each(function (line) {
                vatable_sales += line.vatable_sales;
                vat_amount += line.vat_amount;
                zero_rated += line.zero_rated_sales;
                vat_exempt += line.vat_exempt_sales;
            });
            
            var sales_total = (vatable_sales + vat_amount + zero_rated + vat_exempt).toFixed(2);
            // var sales_total = (vatable_sales + vat_amount + zero_rated + vat_exempt - Math.abs(custom_total_discount)).toFixed(2);
            
            /*
                The following are for combining sequence number information into the
                final sequence number in string to be displayed in the receipt.
            */
            var current_sequence_number_string = this.increment_sequence_number.toString();
            if (this.sale_team_prefix == 'TEST'){
                console.log("TEST present");
                current_sequence_number_string = "0";
            }
            while (current_sequence_number_string.length < 6){
                console.log("current_sequence_number_string.length < 6");
                current_sequence_number_string = "0" + current_sequence_number_string;
            }
            
            if(this.ending_sequence_number > Math.pow(9,6)){
                console.log(this.ending_sequence_number > Math.pow(9,6));
                var length_of_ending_sequence_number = (this.ending_sequence_number.toString()).length;
                while (current_sequence_number_string.length < length_of_ending_sequence_number){
                    current_sequence_number_string = "0" + current_sequence_number_string;
                }
            }

            // Removed unused code

            var first_Data_yr = this.validation_date.getFullYear();
            var sec_Data_yr = Number(this.pos.company.awb_pos_provider_display_valid_until.split('/')[2]);
            var total_year = sec_Data_yr - first_Data_yr;
            var sale_team_prefix = this.pos.team[0].sale_team_prefix_id[1];
            this.final_sequence_number = this.sale_team_prefix + ' ' + current_sequence_number_string;
            var receipt = {
                receipt_number: this.final_sequence_number, //display next receipt number
                sale_team_prefix: sale_team_prefix,
                zero_rated: zero_rated,
                vatable_sales: vatable_sales,
                senior_citizen_pwd_total_with_vat: senior_citizen_pwd_total_with_vat,
                senior_citizen_pwd_total_without_vat: senior_citizen_pwd_total_without_vat,
                senior_citizen_pwd_vat: senior_citizen_pwd_vat,
                senior_citizen_pwd_without_vat: senior_citizen_pwd_without_vat,
                senior_citizen_disc: senior_citizen_disc,
                pwd_citizen_disc: pwd_citizen_disc,
                solo_parent_disc: solo_parent_disc,
                senior_citizen_pwd_total: senior_citizen_pwd_total,
                vat_exempt: vat_exempt,
                vat_amount: vat_amount,
                orderlines: orderlines,
                paymentlines: paymentlines,
                custom_total_discount: custom_total_discount,
                sales_total: sales_total,
                subtotal: this.get_subtotal(),
                total_with_tax: this.get_total_with_tax(),
                total_rounded: this.get_total_with_tax() + this.get_rounding_applied(),
                total_without_tax: this.get_total_without_tax(),
                total_tax: this.get_total_tax(),
                total_paid: this.get_total_paid(),
                total_discount: this.get_total_discount(),
                total_year: total_year,
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
                pricelist: {
                    name: pricelist_name,
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
                machine_info: {
                    min: min,
                    sn: sn,
                    ptu: ptu,
                    remarks: remarks,
                },
                company: {
                    email: company.email,
                    website: company.website,
                    company_registry: company.company_registry,
                    street: company.street,
                    street2: company.street2,
                    city: company.city,
                    state: company.state_id.name,
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
            console.log('receipt',receipt);

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
            return receipt;
        },
        recalculate_discount: function(){
            //this function will be called upon validating the order
            var pricelist = this.pricelist;
            var pricelist_discount = 0;

            this.orderlines.each(function(line){
                /*
                    Overwrite discount of each orderline if there are pricelist discount.
                */

                if(line.discount!=0){
                    /*
                        Check if there is a discount;
                        Check if it is sc_discount;
                            Save amount in appropriate field;
                        Check if it is pwd_discount;
                            Save amount in appropriate field;
                    */
                    if(line.sc_discount != 0){
                        var price_w_quantity = line.price * line.quantity;
                        var sc_discount_amount = price_w_quantity * line.sc_discount/100;

                        line.sc_discount_amount = sc_discount_amount;
                    }
                    if(line.pwd_discount != 0){
                        var price_w_quantity = line.price * line.quantity;
                        var pwd_discount_amount = price_w_quantity * line.pwd_discount/100;

                        line.pwd_discount_amount = pwd_discount_amount;
                    }
                }

                if(line.pos.default_pricelist != line.order.pricelist && !(line.pricelist_discount_amount > 0)){ //if there is an pricelist present
                    // get_price_with_tax_before_pricelist
                    line.pricelist_discount_amount = (line.product.lst_price - line.price) * line.quantity;
                }

                line.get_vat_info();

                console.log("line", line);
            });
        }
    });

    models.Orderline = models.Orderline.extend({
        get_vat_info: function() {
            var price_unit = this.product.lst_price
            var taxtotal = 0;

            var product =  this.get_product();
            var taxes_ids = this.tax_ids || product.taxes_id;
            taxes_ids = _.filter(taxes_ids, t => t in this.pos.taxes_by_id);
            var taxdetail = {};
            var product_taxes = this.get_taxes_after_fp(taxes_ids);

            var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
            _(all_taxes.taxes).each(function(tax) {
                taxtotal += tax.amount;
                taxdetail[tax.id] = tax.amount;
            });
            console.log("taxtotal", taxtotal);
            var temp_vatable = 0;
            var temp_vat_amount = 0;
            var temp_zero_rated = 0;
            var temp_vat_exempt = 0;

            // match taxes_ids to this.pos.taxes_by_id
            // check if vat_exempt
            // if vat_exempt
            // overwrite temp_vat_exempt_sales
            var temp_taxes_by_ids = this.pos.taxes_by_id;
            // this can be simplified by using get_taxes_after_fp() to
            // get the tax_type
            Object.keys(taxdetail).forEach(key => {
                if(Object.keys(temp_taxes_by_ids).includes(key)){
                    // add and check if its != "vatable" but is not false
                    if(temp_taxes_by_ids[key].tax_type == "vat_exempt"){
                        var temp_price_after_discount = this.get_all_prices().priceWithTax;
                        // var original_product_tax = this.get_taxes_after_fp(this.product.taxes_id);
                        // var vat_exempt_all_taxes = this.compute_all(original_product_tax, price_unit, this.get_quantity(), this.pos.currency.rounding);
                        
                        // //if there is a pricelist, compute for that first before vat_exempt
                        // if(this.pricelist_discount_amount != 0){
                        //     var temp_price_after_pricelist = vat_exempt_all_taxes.total_included - this.pricelist_discount_amount;
                        //     vat_exempt_all_taxes = this.compute_all(original_product_tax, temp_price_after_pricelist, 1, this.pos.currency.rounding);
                        // }
                        // temp_vat_exempt = vat_exempt_all_taxes.total_excluded;
                        temp_vat_exempt = temp_price_after_discount;
                        // temp_vat_exempt = this.price * this.quantity;
                        console.log("vat_exempt", temp_taxes_by_ids[key].tax_type);
                    }
                    else if(temp_taxes_by_ids[key].tax_type == "vatable"){
                        var temp_price_after_discount = this.get_all_prices().priceWithTax;
                        // var original_product_tax = this.get_taxes_after_fp(this.product.taxes_id);
                        // var default_price_all_taxes = this.compute_all(original_product_tax, price_unit, this.get_quantity(), this.pos.currency.rounding);
                        
                        var taxtotal = 0;
                        
                        var vatable_all_taxes = this.compute_all(product_taxes, temp_price_after_discount, 1, this.pos.currency.rounding);


                        _(vatable_all_taxes.taxes).each(function(tax) {
                            taxtotal += tax.amount;
                        });

                        temp_vatable = vatable_all_taxes.total_excluded;
                        temp_vat_amount = taxtotal;

                        //if there is a pricelist, compute for that first before vatable
                        // if(this.pricelist_discount_amount != 0){
                        //     console.log("with pricelist");
                        //     var temp_price_after_pricelist = default_price_all_taxes.total_included - this.pricelist_discount_amount;
                        //     var vatable_all_taxes = this.compute_all(original_product_tax, temp_price_after_pricelist, 1, this.pos.currency.rounding);


                        //     _(vatable_all_taxes.taxes).each(function(tax) {
                        //         taxtotal += tax.amount;
                        //     });

                        //     temp_vatable = vatable_all_taxes.total_excluded;
                        //     temp_vat_amount = taxtotal;
                        // }
                        // else{
                        //     _(default_price_all_taxes.taxes).each(function(tax) {
                        //         taxtotal += tax.amount;
                        //     });
                        //     temp_vatable = default_price_all_taxes.total_excluded;
                        //     temp_vat_amount = taxtotal;
                        // }
                        // temp_vatable = vatable_all_taxes.total_excluded;
                        // temp_vat_amount = taxtotal;
                        console.log("vatable", temp_taxes_by_ids[key].tax_type);
                    }
                    else if(temp_taxes_by_ids[key].tax_type == "zero_rated"){
                        var temp_price_after_discount = this.get_all_prices().priceWithTax;
                        
                        // var original_product_tax = this.get_taxes_after_fp(this.product.taxes_id);
                        // var zero_rated_all_taxes = this.compute_all(original_product_tax, price_unit, this.get_quantity(), this.pos.currency.rounding);

                        // //if there is a pricelist, compute for that first before zero_rated
                        // if(this.pricelist_discount_amount != 0){
                        //     var temp_price_after_pricelist = zero_rated_all_taxes.total_included - this.pricelist_discount_amount;
                        //     zero_rated_all_taxes = this.compute_all(original_product_tax, temp_price_after_pricelist, 1, this.pos.currency.rounding);
                        // }

                        temp_zero_rated = temp_price_after_discount;
                        // temp_zero_rated = zero_rated_all_taxes.total_excluded;
                        
                        console.log("zero_rated", temp_taxes_by_ids[key].tax_type);
                    }
                }
            });

            this.vatable_sales = temp_vatable;
            this.vat_amount = temp_vat_amount;
            this.zero_rated_sales = temp_zero_rated;
            this.vat_exempt_sales = temp_vat_exempt;
        },
        // changes the base price of the product for this orderline
        set_unit_price: function(price){
            _super_Orderline.set_unit_price.apply(this, arguments);
            //if vat_exclusive is true, overwrite this.price with tax excluded price
            if(this.is_vat_exclusive == true && (this.sc_discount != 0 || this.pwd_discount != 0)){
                console.log("is vat ex, with sc/pwd discount");
                
                var price_after_pricelist = this.product.get_price(this.order.pricelist, this.get_quantity(), this.get_price_extra())
                var taxes_ids = this.product.taxes_id;
                taxes_ids = _.filter(taxes_ids, t => t in this.pos.taxes_by_id);
                var product_taxes = this.get_taxes_after_fp(taxes_ids);
                                                            
                var all_taxes = this.compute_all(product_taxes, price_after_pricelist, 1, this.pos.currency.rounding);

                this.price = all_taxes.total_excluded;
            }
        },
        initialize: function(attr,options){
            
            this.vatable_sales = 0;
            this.vat_amount = 0;
            this.zero_rated_sales = 0;
            this.vat_exempt_sales = 0;

            this.is_vat_exclusive = false;

            this.sc_discount = 0;
            this.sc_discount_amount = 0;
            this.pwd_discount = 0;
            this.pwd_discount_amount = 0;
            this.is_sc_pressed = false;
            this.is_pwd_pressed = false;
            this.pricelist_discount_amount = 0;
            
            _super_Orderline.initialize.apply(this, arguments);
        },
        init_from_JSON: function(json) {
            this.vatable_sales = json.vatable_sales;
            this.vat_amount = json.vat_amount;
            this.zero_rated_sales = json.zero_rated_sales;
            this.vat_exempt_sales = json.vat_exempt_sales;

            this.is_vat_exclusive = json.is_vat_exclusive;

            this.sc_discount = json.sc_discount;
            this.sc_discount_amount = json.sc_discount_amount;
            this.pwd_discount = json.pwd_discount;
            this.pwd_discount_amount = json.pwd_discount_amount;
            this.is_sc_pressed = false;
            this.is_pwd_pressed = false;
            this.pricelist_discount_amount = json.pricelist_discount_amount;

            _super_Orderline.init_from_JSON.apply(this, arguments);
        },
        export_as_JSON: function() {
            var super_export_as_JSON = _super_Orderline.export_as_JSON.apply(this, arguments);
            
            super_export_as_JSON.vatable_sales = this.vatable_sales;
            super_export_as_JSON.vat_amount = this.vat_amount;
            super_export_as_JSON.zero_rated_sales = this.zero_rated_sales;
            super_export_as_JSON.vat_exempt_sales = this.vat_exempt_sales;
            //update is_vat_exclusive in orderline
            super_export_as_JSON.is_vat_exclusive = this.is_vat_exclusive;

            super_export_as_JSON.sc_discount = this.sc_discount;
            super_export_as_JSON.pwd_discount = this.pwd_discount;
            // regular_discount: ,
            // pricelist_discount: ,
            // promo_discount: ,
            // coupon_discount: ,

            super_export_as_JSON.sc_discount_amount = this.sc_discount_amount;
            super_export_as_JSON.pwd_discount_amount = this.pwd_discount_amount;
            // regular_discount_amount: ,
            super_export_as_JSON.pricelist_discount_amount = this.pricelist_discount_amount;
            // promo_discount_amount: ,
            // coupon_discount_amount: ,
            
            return super_export_as_JSON;
        },
        export_for_printing: function(){
            var super_export_for_printing = _super_Orderline.export_for_printing.apply(this, arguments);
        
            super_export_for_printing.is_vat_exclusive = this.is_vat_exclusive;

            super_export_for_printing.sc_discount = this.sc_discount;
            super_export_for_printing.sc_discount_amount = this.sc_discount_amount;
            super_export_for_printing.pwd_discount = this.pwd_discount;
            super_export_for_printing.pwd_discount_amount = this.pwd_discount_amount;
            super_export_for_printing.pricelist_discount_amount = this.pricelist_discount_amount;
            super_export_for_printing.sc_discount_amount_Str = this.sc_discount_amount.toFixed(2);
            super_export_for_printing.pwd_discount_amount_Str = this.pwd_discount_amount.toFixed(2);
            super_export_for_printing.pricelist_discount_amount_Str = this.pricelist_discount_amount.toFixed(2);

            super_export_for_printing.price_with_tax_before_pricelist = this.get_price_with_tax_before_pricelist();
            
            return super_export_for_printing;
        },
    });
});
