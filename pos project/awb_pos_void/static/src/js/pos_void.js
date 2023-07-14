odoo.define('awb_pos_void.pos_void', function (require) {
'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc')
   	
   	//extended product screen and added the void button.
    const VoidPos = (ProductScreen) =>
       class extends ProductScreen {
           constructor() {
               super(...arguments);
           }
           
           onClickVoid(){
			   this.clearOrderlines()
		   }
        
           async clearOrderlines() {
           	const orders = this.currentOrder;
           	const partner = orders.get_client()
   			console.log(orders)
           	if (orders.get_orderlines().length > 0) {
				   
			const { confirmed, payload } = await this.showPopup('ConfirmPopup', {
							                        title: this.env._t('Empty Cart'),
							                        body: this.env._t('All the items will be cleared and this transaction will be cancelled. Ok to continue?'),
							                        confirmed: true,
							                    });  
			if (confirmed){
				var orderlines = orders.get_orderlines()
				var product_details = []
				var other_details = []
				if (partner){
					other_details.push({'partner_id':partner.id,
										'config_id':orders.pos.config_id,
										'session_id':orders.pos_session_id,
										'user_id':orders.user_id})
									
										
					orderlines.forEach((orderline)=>{
					product_details.push({'product_id':orderline.product.id,
										  'product_description':orderline.product.description,
										  'qty':orderline.quantity,
										  'unit_price':orderline.price,
										  'discount':orderline.discount})
					
					})
					
					rpc.query({
						model: 'pos.void',
		                method: 'create_pos_void',
		                args: [product_details, other_details],
					}).then(function(result){
			               while(orders.get_selected_orderline()) {
			                    orders.remove_orderline(orders.get_selected_orderline())
			                } 
					})			
										
				} else {
					this.showPopup('ErrorPopup', {
							                        title: this.env._t('Warning'),
							                        body: this.env._t('Please Select Customer.'),
							                        confirmed: true,
							       });
				}
			
			} else{
				console.log('order is not cancelled')
			}
           	} 
           }
           
       };
      
       
     
    Registries.Component.extend(ProductScreen, VoidPos);
   	return VoidPos;
});