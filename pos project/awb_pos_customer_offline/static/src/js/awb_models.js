odoo.define('awb_pos_customer_offline.awb_models', function (require) {
"use strict";
	var PosDB = require('point_of_sale.DB');
	const models = require('point_of_sale.models');
	
	PosDB.include({
		name: 'openerp_pos_db', //the prefix of the localstorage data
	    limit: 100,  // the maximum number of results returned by a search
	    init: function (options) {
	    	this._super(options);
			this.posCustomerOffline = [];
			this.posCustomerOfflineDup = [];
	    },
	    /*TO SET RES PARTNER MODEL, FIELDS, DOMAIN*/
		setPosCustomerOffline: function (details) {
			this.posCustomerOffline.push(details)
		},
		setPosCustomerOfflineDup: function (details) {
			this.posCustomerOfflineDup.push(details)
		},
	});
	
	models.PosModel = models.PosModel.extend({
		/*overide base method, for creating customer and place order*/
		push_orders: async function (order, opts) {
		if (this.env.pos.config.awb_customer_offline) {
			for (let i = 0; i < this.env.pos.db.posCustomerOffline.length; i++) {
				//var prevId = this.env.pos.db.posCustomerOffline[i].id
				var newCustomer = {}
				newCustomer['id'] = false
				newCustomer['name'] = this.env.pos.db.posCustomerOffline[i].name
				newCustomer['email'] = this.env.pos.db.posCustomerOffline[i].email
				newCustomer['property_product_pricelist'] = this.env.pos.db.posCustomerOffline[i].property_product_pricelist 
				newCustomer['city'] = this.env.pos.db.posCustomerOffline[i].city
				newCustomer['country_id'] = this.env.pos.db.posCustomerOffline[i].country_id
				newCustomer['zip'] = this.env.pos.db.posCustomerOffline[i].zip
				newCustomer['state_id'] = this.env.pos.db.posCustomerOffline[i].state_id
				newCustomer['street'] = this.env.pos.db.posCustomerOffline[i].street
				
				let partnerId = await this.rpc({
	                    model: 'res.partner',
	                    method: 'create_from_ui',
	                    args: [newCustomer],
	                });
	            console.log(partnerId)
	            
			}
			opts = opts || {};
	        var self = this;
	
	        if (order) {
	            this.db.add_order(order.export_as_JSON());
	        }
	
	        return new Promise((resolve, reject) => {
	            self.flush_mutex.exec(async () => {
	                try {
	                    resolve(await self._flush_orders(self.db.get_orders(), opts));
	                } catch (error) {
	                    reject(error);
	                }
	            });
	        });
		} else {
			opts = opts || {};
	        var self = this;
	
	        if (order) {
	            this.db.add_order(order.export_as_JSON());
	        }
	
	        return new Promise((resolve, reject) => {
	            self.flush_mutex.exec(async () => {
	                try {
	                    resolve(await self._flush_orders(self.db.get_orders(), opts));
	                } catch (error) {
	                    reject(error);
	                }
	            });
	        });
		}
        
    },
		
	})
});