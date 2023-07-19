odoo.define("blog_topic2.PartnerOrderSummary", function (require) {
const FormRenderer = require("web.FormRenderer");
const { Component } = owl;
const { ComponentWrapper } = require("web.OwlCompatibility");
const { useState } = owl;
var core = require('web.core');
var QWeb = core.qweb;
var rpc = require('web.rpc');
var _t = core._t;


class CustomerOrderSummary extends Component {

partner = useState({});
constructor(self, partner) {
super();
this.partner = partner;

}
};

class potentialgem extends Component {

potential_gem = useState({});
constructor(self, potential_gem) {
super();
this.potential_gem = potential_gem;
console.log('potential',potential_gem)
}
};
class highpotential extends Component {

high_potential = useState({});
constructor(self, high_potential) {
super();
this.high_potential = high_potential;
}
};
class star extends Component {
star = useState({});
constructor(self, star) {
super();
this.star = star;
console.log('star',star)
}
};
class inconsistent extends Component {
inconsistent = useState({});
constructor(self, inconsistent) {
super();
this.inconsistent = inconsistent;
}
};
class corep extends Component {
corep = useState({});
constructor(self, corep) {
super();
this.corep = corep;
}
};
class highp extends Component {
highp = useState({});
constructor(self, highp) {
super();
this.highp = highp;
}
};
class risk extends Component {
risk = useState({});
constructor(self, risk) {
super();
this.risk = risk;
}
};
class average extends Component {
average = useState({});
constructor(self, average) {
super();
this.average = average;
}
};
class solid extends Component {
solid = useState({});
constructor(self, solid) {
super();
this.solid = solid;
}
};
class currectapp extends Component {
currectapp = useState({});
constructor(self, currectapp) {
super();
this.currectapp = currectapp;
console.log('curentapp',currectapp)
}
};


Object.assign(CustomerOrderSummary, {
template: "blog_topic2.CustomerOrderSummary"
});
Object.assign(potentialgem, {
template: "potential_gem"
});
Object.assign(highpotential, {
template: "high_potential"
});
Object.assign(star, {
template: "star"
});
Object.assign(inconsistent, {
template: "inconsistent"
});
Object.assign(corep, {
template: "corep"
});
Object.assign(highp, {
template: "highp"
});
Object.assign(risk, {
template: "risk"
});
Object.assign(average, {
template: "average"
});
Object.assign(solid, {
template: "solid"
});
Object.assign(currectapp, {
template: "currectapp"
});

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
(new ComponentWrapper(
this,
CustomerOrderSummary,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
potentialgem,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
highpotential,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
star,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
inconsistent,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
corep,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
highp,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
risk,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
average,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
solid,
  useState(data)
)).mount(element);
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
(new ComponentWrapper(
this,
currectapp,
  useState(data[0])
)).mount(element);
});
}


}

});



});