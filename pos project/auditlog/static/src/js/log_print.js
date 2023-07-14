odoo.define('auditlog.log_print', function (require) {
"use strict";

    const components = {
        ActionMenus: require('web.ActionMenus'),
    };
	var rpc = require('web.rpc')
    const { patch } = require('web.utils');

	/*Patching the action menu*/
    patch(components.ActionMenus.prototype, 'auditlog.log_print', {
		
       /* async willStart() {
            this._super(...arguments);
            this._checkReprint(this)
            this.actionItems = await this._setActionItems(this.props);
            this.printItems = await this._setPrintItems(this.props);

        },*/
	 _onItemSelected(ev) {
            ev.stopPropagation();
            const { item } = ev.detail;
            if (item.callback) {
                item.callback([item]);
            } else if (item.action) {
                this._executeAction(item.action);
            } else if (item.url) {
                // Event has been prevented at its source: we need to redirect manually.
                this.env.services.navigate(item.url);
            }
            const model=ev.originalComponent.env.view.model
            const active_ids = this.props.activeIds[0]
            const action_name = ev.originalComponent.props.description
            
            var for_ev =" "
	            rpc.query({
		                  model: 'auditlog.log',
	                    method: 'print_log',
	                    args: [for_ev,model,active_ids,action_name],
	                   
		            }).then(function () {
		               
		            });
           
           
        },
		async _setPrintItems(props) {
			
            const printActions = props.items.print || [];
            const printItems = printActions.map(
                action => ({ action, description: action.name, key: action.id })
            );
            
            return printItems;
        },
        
       /* async willUpdateProps(nextProps) {
            this._super(...arguments);
            this._checkReprintIt(nextProps)
            this.actionItems = await this._setActionItems(nextProps);
            this.printItems = await this._setPrintItems(nextProps);
        },*/
		
		  
		/*checking the reprint condition while willstart*/
		/*async _checkReprint(target){
			debugger
			var activeIds = target.props.activeIds
			var con = 'context' in target
			if (con) {
				var modelCheck = target.context
			} else {
				var modelCheck = []
			}
			var modelCheck = target.props.context
			var modelKey = 'params' in modelCheck
			if (modelKey == false) {
				var model = target.env.view.base_model
			} else {
				var model = target.props.context.params.model
			}
			var len = activeIds.length
			var displayName = ['Invoices', 'Receipts']
			var dName = this.env.action.display_name 
			if ((len === 1) && (model == 'account.move') && (displayName.includes(dName) )){
				await rpc.query({
	                model: 'account.move',
	                method: 'js_assign_reprint_rename',
	                args: [activeIds[0] ,this.props],
	            }).then(function (result) {
	                if (result == true) {
						/*Checked the product node is present or not*/
						/*var productNode = $("[data-original-title='Printing options']");
						if (productNode[0]) {
							productNode[0].innerHTML = "<i class=\"fa fa-print small mr-1\"></i><span class=\"o_dropdown_title\">Reprint</span>"
						}
					} else {
						var productNode = $("[data-original-title='Printing options']");
						productNode[0].innerHTML = "<i class=\"fa fa-print small mr-1\"></i><span class=\"o_dropdown_title\">Print</span>"
						 
					}
	                
	            });
            } else {
				var productNode = $("[data-original-title='Printing options']");
				productNode[0].innerHTML = "<i class=\"fa fa-print small mr-1\"></i><span class=\"o_dropdown_title\">Print</span>"
			}
		},*/
		
		/*checking the reprint condition while nextupdate*/
		/*async _checkReprintIt(target){
			debugger
			var activeIds = target.activeIds
			var con = 'context' in target
			if (con) {
				var modelCheck = target.context
			} else {
				var modelCheck = []
			}
			
			var modelKey = 'params' in modelCheck
			if (modelKey == false) {
				var model = this.env.view.base_model
			} else {
				var model = target.props.context.params.model
			}
			var len = activeIds.length
			var displayName = ['Invoices', 'Receipts']
			var dName = this.env.action.display_name 
			if ((len === 1) && (model == 'account.move') && (displayName.includes(dName))){
				await rpc.query({
	                model: 'account.move',
	                method: 'js_assign_reprint_rename',
	                args: [activeIds[0] ,this.props],
	            }).then(function (result) {
	                if (result == true) {
						/*Checked the product node is present or not*/
						/*var productNode = $("[data-original-title='Printing options']");
						if (productNode[0]) {
							productNode[0].innerHTML = "<i class=\"fa fa-print small mr-1\"></i><span class=\"o_dropdown_title\">Reprint</span>"
						}
						
					} else {
						var productNode = $("[data-original-title='Printing options']");
						productNode[0].innerHTML = "<i class=\"fa fa-print small mr-1\"></i><span class=\"o_dropdown_title\">Print</span>"

					}
	                
	            });
            } else {
				var productNode = $("[data-original-title='Printing options']");
				productNode[0].innerHTML = "<i class=\"fa fa-print small mr-1\"></i><span class=\"o_dropdown_title\">Print</span>"
			}
		},*/
		
		/*updating the value to record*/
		/*_onItemSelected(ev) {
			this._super(...arguments);
			var activeIds = this.props.activeIds
			var modelCheck = this.props.context
			var modelKey = 'params' in modelCheck
			if (modelKey == false) {
				var model = this.env.view.base_model
			} else {
				var model = this.props.context.params.model
			}
			var len = activeIds.length
			if ((len === 1) && (model == 'account.move')){
				rpc.query({
	                model: 'account.move',
	                method: 'js_assign_reprint',
	                args: [activeIds[0] ,this.props],
	            }).then(function () {
	                console.log('Reprint value Updated')
	            });
            }
		}*/
    });

	
});