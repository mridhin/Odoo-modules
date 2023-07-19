odoo.define("web_access_rule_buttons.main", function (require) {
    "use strict";
    var FormController = require("web.FormController");
    FormController.include({
       async _update(state, params) {
            await this._super(state, params);
                this.show_hide_edit_button();
        },
        show_hide_edit_button: function (edit_disabled) {
            if (this.modelName === 'res.users') {
                var record = this.model.get(this.handle, {raw: true});
                var session = require('web.session');
                var current_user = session.uid
                var user_id = record["data"]["id"]
                var button = this.$buttons.find(".o_form_button_edit")
                if (current_user === user_id) {
                    var edit_disabled = true
                    button.prop("hidden", edit_disabled);
                    this.activeActions.edit = false;                                                                                                                                                                                                                                                                                                                                              
                }
                else{
                    var edit_disabled = false
                    button.prop("hidden", edit_disabled);
                    this.activeActions.edit = true;
                }
             }
        },
    });

});