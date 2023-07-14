odoo.define('awb_pos_sc_pwdID.scpwdPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    // formerly TextInputPopupWidget
    class SCpwdPopup extends AbstractAwaitablePopup {
    
    	constructor() {
            super(...arguments);
            this.state = useState({ inputValue: this.props.startingValue });
            this.inputRef = useRef('input');
        }
        mounted() {
            this.inputRef.el.focus();
        }
        getPayload() {
            return this.state.inputValue;
        }
    
    }
    
    
    SCpwdPopup.template = 'SCpwdPopup';
    SCpwdPopup.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: '',
        body: '',
    };
	
    Registries.Component.add(SCpwdPopup);

    return SCpwdPopup;
});
