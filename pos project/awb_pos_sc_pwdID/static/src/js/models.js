odoo.define('awb_pos_sc_pwdID.models', function (require) {
var models = require('point_of_sale.models');

// models.load_fields('pos.order', 'sc_pwd_id');
models.load_fields('res.partner', ['sc_id', 'pwd_id']);

});
