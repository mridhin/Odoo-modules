odoo.define('color_theme_backend_cqt.change_color_backend', function (require) {
    "use strict";

    var session = require('web.session');
    var rpc = require('web.rpc');

    var uid = session.user_id
    var user = {}
    user.id = uid

    if (user.id) {
        rpc.query({
            model: 'res.users',
            method: 'get_color',
            args: [user],
        }).then(function (data) {
            if (data.employee_theme_color) {
                console.log(data.employee_theme_color)
                let root = document.documentElement
                root.style.setProperty('--o-enterprise-color', data.employee_theme_color)
            }
        });
    }
})