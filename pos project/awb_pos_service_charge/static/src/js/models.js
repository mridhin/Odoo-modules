odoo.define('awb_pos_service_charge.models', function (require) {

const models = require('point_of_sale.models');
const { useState } = owl.hooks;
var _super_order = models.Order.prototype;

models.Order = models.Order.extend({

		_update_service_amount() {
        
        	// ----------------------------------
            var product = this.pos.db.get_product_by_id(this.pos.config.service_product_id[0]);
            var lines = this.pos.get_order().get_orderlines();
            var line = lines.filter(e => e.get_product() == product);
            
            var selectedOrderline = this.pos.get_order().get_selected_orderline();
            var service_charge = 0
            var service_charge_final = 0
            var is_service_percentage = false
            
            for (var i = 0; i < line.length; i++) {
            		
            		is_service_percentage = line[i].is_service_percentage
            		
            		if (line[i].is_service_percentage) {
            		
            			service_charge = parseInt(line[i].service_percentage)
            		
            		} else {
            			service_charge = parseInt(line[i].service_amount)
            		}
            		
                    // line[i].order.remove_orderline(line[i]);
                    line[i].set_unit_price(0);
                    line[i].set_quantity(0);
                    line[i].discount = 0;
                    line[i].discountStr = '0';
                    line[i].quantityStr = '';
                    line[i].is_service_charge = true;
                    
                }
            
	            var total_amount = this.pos.get_order().get_total_with_tax()
	            
	            if (is_service_percentage && service_charge) {
	            
	            	service_charge_final = (parseInt(line[0].service_percentage) / 100.0)*total_amount
	            
	            } else if (!is_service_percentage && service_charge) {
	            
	            	service_charge_final = parseInt(line[0].service_amount)
	            
	            }
	            
	           
	            var lines = this.pos.get_order().get_orderlines();
	            var line = lines.filter(e => e.get_product() == product);
				
				if (line.length > 0) {
					
					line[0].set_unit_price(service_charge_final);
					line[0].set_quantity(1);
					line[0].discount = 0;
					line[0].discountStr = '0';
					line[0].quantityStr = '';
					line[0].is_service_charge = true;
				
					if (is_service_percentage && service_charge) {
		            		line[0].is_service_percentage = is_service_percentage
		            		line[0].service_percentage = service_charge
		            		line[0].quantityStr = service_charge + "%";
		            		produt_name = line[0].get_product().display_name + " " + service_charge + "%";
		            		line[0].set_full_product_name(produt_name);
		            	} else {
	            			line[0].is_service_percentage = is_service_percentage
		            		line[0].service_amount = service_charge
		            		line[0].quantityStr = "Amount "+service_charge;
	            		}
	            	}
	            	
	         // ----------------------------------
        },
        
     get_service_charge: function() {
     	var product = this.pos.db.get_product_by_id(this.pos.config.service_product_id[0]);
     	var line = this.pos.get_order().get_orderlines().filter(e => e.get_product() == product);
     	if (line.length > 0) {
     		return line[0].price
     	} else {
     		return 0;
     	}
     },

	remove_orderline: function( line ){
	        this.assert_editable();
	        var product = this.pos.db.get_product_by_id(this.pos.config.service_product_id[0]);
	        var set_line = this.orderlines.filter(e => e.get_product() != product);
	        
	        if (line.get_product() == product) {
	        	
	        	if (this.orderlines.length == 1) {
	        	
	        		this.orderlines.remove(line);
	        		this.select_orderline(this.get_last_orderline());
	        		
	        	} else {
	        	   
	        	   var set_line = this.orderlines.filter(e => e.get_product() != product);
		           if (set_line.length > 0) {
		           		set_line[0].order.select_orderline(set_line[0]);
		           }				
	        	}
	        
	        } else {
	        
	        	this.orderlines.remove(line);
	        	this.select_orderline(this.get_last_orderline());
	        	
	        	var set_line = this.orderlines.filter(e => e.get_product() != product);
	        	if (set_line.length > 0) {
		        	set_line[0].order.select_orderline(set_line[0]);
		          }
	        }
        
    	},
   })
   
    var _orderline_super = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
    
    	initialize: function (attr, options) {
    		this.is_service_charge = false;
            this.is_service_percentage = true;
            this.service_amount = 0;
            this.service_percentage = 0;
            _orderline_super.initialize.apply(this, arguments);
        },
        
    	init_from_JSON: function (json) {
    
    		this.is_service_charge = json.is_service_charge;
            this.is_service_percentage = json.is_service_percentage;
            this.service_amount = json.service_amount;
            this.service_percentage = json.service_percentage;
            
            _orderline_super.init_from_JSON.apply(this, [json]);
        },
        
        export_as_JSON: function() {
        
            var super_export_as_JSON = _orderline_super.export_as_JSON.apply(this, arguments);
            
            super_export_as_JSON.is_service_charge = this.is_service_charge;
            super_export_as_JSON.is_service_percentage = this.is_service_percentage;
            super_export_as_JSON.service_amount = this.service_amount;
            super_export_as_JSON.service_percentage = this.service_percentage;
            
            return super_export_as_JSON;
            
       },     
       
       
    })
   

});
