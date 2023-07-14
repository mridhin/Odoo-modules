odoo.define('awb_pos_sc_pwdID.ClientDetailsEdit', function(require) {
    "use strict";

    const { _t } = require('web.core');

    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    const _super_client_details_edit = ClientDetailsEdit.prototype;

    const ScPwdClientDetailsEdit = ClientDetailsEdit => class extends ClientDetailsEdit {
        setup(){
            var prev_this = this;
            
            const observer = new MutationObserver(function(){
                console.log('observer called')
                if (document.getElementById('check_sc_pwd_checkbox')){
                    console.log('element exists')
                    prev_this.hideScPwdFields();
                    prev_this.highlightFields();
                    observer.disconnect();
                }
            })

            const target = document.querySelector('.subwindow');
            const config = {attributes: true, childList: true, subtree: true};

            observer.observe(target, config);
        }

        captureChange(event) {
            _super_client_details_edit.captureChange.apply(this, arguments);
            if(event.target.type == 'checkbox'){
                this.changes[event.target.name] = event.target.checked;
            }
        }

        saveChanges(){
            //TODO: validate if both sc_id and pwd_id is blank
            //      if(
            //      (!props.sc_id && !this.changes.sc_id || this.changes.sc_id == '') &&
            //      (!props.pwd_id && !this.changes.pwd_id || this.changes.pwd_id == '')
            //      )
            //      check for:
            //      if the user is sc/pwd:
            //      - fetch from record (this.props.partner)
            //      - fetch from changes (this.changes) (if not true)
            //      - if == ''
            
            //TODO: remove/hide id fields in the backend if check_sc_pwd is false

            // check if user is sc/pwd then continue with the validation:
            // should be true in record and is not changed
            // or true in change 
            
            if(this.props.partner.check_sc_pwd && !this.changes.check_sc_pwd || this.changes.check_sc_pwd){
                console.log('user is sc/pwd');
                if( //if both sc_id and pwd_id records or changes are blank or false
                    (!this.props.partner.sc_id && !this.changes.sc_id || this.changes.sc_id == '') &&
                    (!this.props.partner.pwd_id && !this.changes.pwd_id || this.changes.pwd_id == '')
                ){
                    //disable check_sc_pwd so that the user cannot trick the saving system
                    //using the function .click() will simulate a user clicking the checkbox
                    //which will also trigger the onchange function attached to the checkbox
                    //which includes hiding the sc/pwd fields as well as registering the changes.
                    document.getElementById('check_sc_pwd_checkbox').click();

                    return this.showPopup('ErrorPopup', {
                        title: _t('SC or PWD IDs are Required'),
                    });
                }
            }
            else{
                console.log('user is not sc/pwd')
            }
            
            _super_client_details_edit.saveChanges.apply(this,arguments);

        }

        isScPwdPressed(orderline){
            for(let line in orderline){
                if (orderline[line].is_sc_pressed || orderline[line].is_pwd_pressed){
                    return true;
                }
            }
            return false;
        }

        hideScPwdFields(){
            console.log('hideScPwdFields() function called');
            let check_sc_pwd_checkbox_status = document.getElementById('check_sc_pwd_checkbox');
            let sc_pwd_fields = document.getElementsByClassName('sc-pwd-fields');
            if (check_sc_pwd_checkbox_status.checked){
                for(let i = 0; i < sc_pwd_fields.length; i++){
                    sc_pwd_fields[i].hidden = false;
                }
            }
            else {
                for(let i = 0; i < sc_pwd_fields.length; i++){
                    sc_pwd_fields[i].hidden = true;
                }
            }
        }

        highlightFields(){
            var orderline = this.env.pos.get_order().get_orderlines();
            if(orderline.length != 0){ //to check if there is an orderline
                var is_sc_pwd_pressed = this.isScPwdPressed(orderline);
            }

            if(is_sc_pwd_pressed){
                console.log('is sc pwd pressed');
                document.getElementById('sc_pwd_checkbox_label').style.color = "red";
                document.getElementsByName('sc_id')[0].style.background = "#fad1d0";
                document.getElementsByName('pwd_id')[0].style.background = "#fad1d0";
            }
            else {
                console.log('is not pressed');
                document.getElementById('sc_pwd_checkbox_label').style.color = "";
                document.getElementsByName('sc_id')[0].style.background = "";
                document.getElementsByName('pwd_id')[0].style.background = "";
            }
        }
        
        showIDs(event){
            // this function is triggered if check_sc_pwd is changed
            
            this.hideScPwdFields();
            this.captureChange(event);
        }
    }
    
    Registries.Component.extend(ClientDetailsEdit, ScPwdClientDetailsEdit);

    return ClientDetailsEdit;
});