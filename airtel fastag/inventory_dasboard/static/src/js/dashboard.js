odoo.define('inventory_dashboard.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var AppraisalDashboard = AbstractAction.extend({
    template: 'inventory_dashboard',

     events: {
         'click .show_all_transfer': '_onClick_show_all_transfer',
         'click .show_assign_transfer': '_onClick_show_assign_transfer',
         'click .show_ackw_transfer': '_onClick_show_ackw_transfer',
         'click .show_cancel_transfer': '_onClick_show_cancel_transfer',
         'click .show_declined_transfer': '_onClick_show_declined_transfer',

    },

    init: function(parent, context) {
        this._super(parent, context);
        this.transfer_id = []
        this.product_id = []
        this.report_id = []
    },

    start: function() {
        var self = this;
        this.set("title", 'Dashboard');

        return this._super().then(function() {
            self.render_dashboards();

        });
    },

    willStart: function() {
        var self = this;
        return $.when(this._super()).then(function() {
             return self.fetch_data();
        });
    },

    fetch_data: function() {
        var self = this;
        var def1 =  this._rpc({
                model: 'stock.picking',
                method: 'get_transfer_list'
            }).then(function(result) {
                self.transfer_id = result;
                console.log("Invalid Delta:", result);
        });
        var def2 =  this._rpc({
                model: 'product.template',
                method: 'get_product_list'
            }).then(function(result) {
                self.product_id = result;
                console.log("Invalid Delta:", result);
        });
        var def3 =  this._rpc({
                model: 'all.transfer.report',
                method: 'get_report_list'
            }).then(function(result) {
                self.report_id = result;

        });
        return $.when(def1,def2,def3);
    },

    render_dashboards: function() {
        var self = this;



         self.$('.o_transfer').append(QWeb.render('TransferChart', {count: self.transfer_id}));
         self.$('.o_product').append(QWeb.render('ProductChart', {count: self.product_id}));
         self.$('.o_report').append(QWeb.render('ReportChart', {count: self.report_id}));
            console.log('widget',self.transfer_id);
    },

    _onClick_show_all_transfer : function(e){
                var self = this
                return self._rpc({
                    model: 'stock.picking',
                    method: 'show_transfer_lists',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'stock.picking',
                    name:_t('All Transfer'),
                    view_mode:'tree',
//                    view_id: result[1],
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['id','in',result]]});
                });

    },
    _onClick_show_assign_transfer : function(e){
                var self = this
                return self._rpc({
                    model: 'stock.picking',
                    method: 'show_assign_transfer',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'stock.picking',
                    name:_t('Assigned Transfer'),
                    view_mode:'tree',
//                    view_id: result[1],
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['id','in',result]]});
                });

    },
    _onClick_show_ackw_transfer : function(e){
                var self = this
                return self._rpc({
                    model: 'stock.picking',
                    method: 'show_ackw_transfer',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'stock.picking',
                    name:_t('Acknowledge Transfer'),
                    view_mode:'tree',
//                    view_id: result[1],
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['id','in',result]]});
                });

    },
    _onClick_show_cancel_transfer : function(e){
                var self = this
                return self._rpc({
                    model: 'stock.picking',
                    method: 'show_cancel_transfer',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'stock.picking',
                    name:_t('Canceled Transfer'),
                    view_mode:'tree',
//                    view_id: result[1],
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['id','in',result]]});
                });

    },
    _onClick_show_declined_transfer : function(e){
                var self = this
                return self._rpc({
                    model: 'stock.picking',
                    method: 'show_declined_transfer',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'stock.picking',
                    name:_t('Declined Transfer'),
                    view_mode:'tree',
//                    view_id: result[1],
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['id','in',result]]});
                });

    },

});


core.action_registry.add('inventory_dashboard', AppraisalDashboard);

return AppraisalDashboard;

});