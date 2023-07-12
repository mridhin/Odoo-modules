odoo.define('9_box_appraisal.formview', function (require) {
const AbstractAction = require('web.AbstractAction');
const core = require('web.core');
const FormRenderer = require("web.FormRenderer");
var _t = core._t;
var QWeb = core.qweb;

FormRenderer.include({
events: {
    "click .list_potential_gem": "_onClick_list_potential_gem",
    'click .list_high_potential': '_onClick_list_high_potential',
    'click .list_star': '_onClick_list_star',
    'click .list_inconsistent': '_onClick_list_inconsistent',
    'click .list_core': '_onClick_list_core',
    'click .list_high': '_onClick_list_high',
    'click .list_risk': '_onClick_list_risk',
    'click .list_average': '_onClick_list_average',
    'click .list_solid': '_onClick_list_solid',
},

_onClick_list_potential_gem : function (e){
                var self = this
                var data = this.state['data'].id
                    console.log('self',data)
                    return self._rpc({
                    model: 'employee.list',
                    method: 'search_read',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'employee.list',
                    name:_t('Potential Gem'),
                    view_mode:'tree',
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['appraisal_name','=',data],['category','=','hp_lp']]});
                });

    },
_onClick_list_high_potential : function (e){
                var self = this
                var data = this.state['data'].id
                    console.log('self',data)
                    return self._rpc({
                    model: 'employee.list',
                    method: 'search_read',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'employee.list',
                    name:_t('High Potential'),
                    view_mode:'tree',
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['appraisal_name','=',data],['category','=','hp_mp']]});
                });

    },
_onClick_list_star : function (e){
                var self = this
                var data = this.state['data'].id
                    console.log('self',data)
                    return self._rpc({
                    model: 'employee.list',
                    method: 'search_read',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'employee.list',
                    name:_t('Star'),
                    view_mode:'tree',
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['appraisal_name','=',data],['category','=','hp_hp']]});
                });

},
_onClick_list_inconsistent : function (e){
                var self = this
                var data = this.state['data'].id
                    console.log('self',data)
                    return self._rpc({
                    model: 'employee.list',
                    method: 'search_read',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'employee.list',
                    name:_t('Inconsistent'),
                    view_mode:'tree',
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['appraisal_name','=',data],['category','=','mp_lp']]});
                });

},
_onClick_list_core : function (e){
                var self = this
                var data = this.state['data'].id
                    console.log('self',data)
                    return self._rpc({
                    model: 'employee.list',
                    method: 'search_read',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'employee.list',
                    name:_t('Core Player'),
                    view_mode:'tree',
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['appraisal_name','=',data],['category','=','mp_mp']]});
                });

},
_onClick_list_high : function (e){
                var self = this
                var data = this.state['data'].id
                    console.log('self',data)
                    return self._rpc({
                    model: 'employee.list',
                    method: 'search_read',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'employee.list',
                    name:_t('High Performer'),
                    view_mode:'tree',
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['appraisal_name','=',data],['category','=','mp_hp']]});
                });

},
_onClick_list_risk : function (e){
                var self = this
                var data = this.state['data'].id
                    console.log('self',data)
                    return self._rpc({
                    model: 'employee.list',
                    method: 'search_read',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'employee.list',
                    name:_t('Risk'),
                    view_mode:'tree',
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['appraisal_name','=',data],['category','=','lp_lp']]});
                });

},
_onClick_list_average : function (e){
                var self = this
                var data = this.state['data'].id
                    console.log('self',data)
                    return self._rpc({
                    model: 'employee.list',
                    method: 'search_read',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'employee.list',
                    name:_t('High Performer'),
                    view_mode:'tree',
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['appraisal_name','=',data],['category','=','lp_mp']]});
                });

},
_onClick_list_solid : function (e){
                var self = this
                var data = this.state['data'].id
                    console.log('self',data)
                    return self._rpc({
                    model: 'employee.list',
                    method: 'search_read',

                }).then(function(result) {

                    return self.do_action({
                    res_model:'employee.list',
                    name:_t('High Performer'),
                    view_mode:'tree',
                    views:[[false,'list']],
                    type:'ir.actions.act_window',
                    target:'new',
                    context:{'create':false,'edit':false},
                    domain:[['appraisal_name','=',data],['category','=','lp_hp']]});
                });

},
async _renderView() {

await this._super(...arguments);
for(const element of this.el.querySelectorAll(".o_partner_order_summary")) {
this._rpc({
model: "period",
method: "search_read",
domain: [
                ['period_id', '=', this.state.data.id],
            ['drop','=',false]
            ]
}).then(
data => {
self.$('.o_partner_order_summary').append(QWeb.render('blog_topic2.CustomerOrderSummary', {widget:data}));
});
}
for(const element of this.el.querySelectorAll(".o_potential_gem")) {
this._rpc({
model: "employee.list",
method: "search_read",
domain: [
                ['appraisal_name', '=', this.state.data.id],
                ['category', '=', 'hp_lp']

            ]
}).then(
data => {
self.$('.o_potential_gem').append(QWeb.render('potential_gem', {potential_gem:data}));
});
}
for(const element of this.el.querySelectorAll(".o_high_potential")) {
this._rpc({
model: "employee.list",
method: "search_read",
domain: [
                ['appraisal_name', '=', this.state.data.id],
                ['category', '=', 'hp_mp']

            ]
}).then(
data => {
self.$('.o_high_potential').append(QWeb.render('high_potential', {high_potential:data}));
});
}
for(const element of this.el.querySelectorAll(".o_star")) {
this._rpc({
model: "employee.list",
method: "search_read",
domain: [
                ['appraisal_name', '=', this.state.data.id],
                ['category', '=', 'hp_hp']

            ]
}).then(
data => {
self.$('.o_star').append(QWeb.render('star', {star:data}));
});
}
for(const element of this.el.querySelectorAll(".o_inconsistent")) {
this._rpc({
model: "employee.list",
method: "search_read",
domain: [
                ['appraisal_name', '=', this.state.data.id],
                ['category', '=', 'mp_lp']

            ]
}).then(
data => {
self.$('.o_inconsistent').append(QWeb.render('inconsistent', {inconsistent:data}));
});
}
for(const element of this.el.querySelectorAll(".o_core")) {
this._rpc({
model: "employee.list",
method: "search_read",
domain: [
                ['appraisal_name', '=', this.state.data.id],
                ['category', '=', 'mp_mp']

            ]
}).then(
data => {
self.$('.o_core').append(QWeb.render('corep', {corep:data}));
});
}
for(const element of this.el.querySelectorAll(".o_highp")) {
this._rpc({
model: "employee.list",
method: "search_read",
domain: [
                ['appraisal_name', '=', this.state.data.id],
                ['category', '=', 'mp_hp']

            ]
}).then(
data => {
self.$('.o_highp').append(QWeb.render('highp', {highp:data}));
});
}
for(const element of this.el.querySelectorAll(".o_risk")) {
this._rpc({
model: "employee.list",
method: "search_read",
domain: [
                ['appraisal_name', '=', this.state.data.id],
                ['category', '=', 'lp_lp']

            ]
}).then(
data => {
self.$('.o_risk').append(QWeb.render('risk', {risk:data}));
});
}
for(const element of this.el.querySelectorAll(".o_average")) {
this._rpc({
model: "employee.list",
method: "search_read",
domain: [
                ['appraisal_name', '=', this.state.data.id],
                ['category', '=', 'lp_mp']

            ]
}).then(
data => {
self.$('.o_average').append(QWeb.render('average', {average:data}));
});
}
for(const element of this.el.querySelectorAll(".o_solid")) {
this._rpc({
model: "employee.list",
method: "search_read",
domain: [
                ['appraisal_name', '=', this.state.data.id],
                ['category', '=', 'lp_hp']

            ]
}).then(
data => {
self.$('.o_solid').append(QWeb.render('solid', {solid:data}));
});
}
for(const element of this.el.querySelectorAll(".o_appraisal")) {
this._rpc({
model: "appraisal.period",
method: "search_read",
domain: [
                ['id', '=', this.state.data.id]
            ]
}).then(
data => {
console.log('dataapp',data)
self.$('.o_appraisal').append(QWeb.render('currectapp', {currectapp:data[0]}));
});
}

}

});
console.log('comp', FormRenderer)
});