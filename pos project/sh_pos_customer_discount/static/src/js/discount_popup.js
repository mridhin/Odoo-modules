/** @odoo-module **/
import AbstractAwaitablePopup from 'point_of_sale.AbstractAwaitablePopup';
import Registries from 'point_of_sale.Registries';
import PosComponent from 'point_of_sale.PosComponent';
import ControlButtonsMixin from 'point_of_sale.ControlButtonsMixin';
import NumberBuffer from 'point_of_sale.NumberBuffer';
import { useListener } from 'web.custom_hooks';
import { onChangeOrder, useBarcodeReader } from 'point_of_sale.custom_hooks';
const { useState } = owl.hooks;
const ProductScreen = require('point_of_sale.ProductScreen');

/*extended the product screen to set the taxes for vat output*/
const clickProductScreen = (ProductScreen) =>
	class extends ProductScreen {
		constructor() {
			super(...arguments);
		}

		async _clickProduct(event) {
			if (!this.currentOrder) {
				this.env.pos.add_new_order();
			}
			const product = event.detail;
			const options = await this._getAddProductOptions(product);
			// Do not add product if options is undefined.
			if (!options) return;

			// Set merge to false to disable auto stacking of products
			// upon clicking it.
			Object.assign(options, {
				merge: false,
			});

			// Removed to prevent overwriting product taxes upon clicking
			// if (product.taxes_id[0] == 2) {
			// 	for (let k = 0; k < product.pos.taxes.length; k++) {
			// 		if (product.pos.taxes[k].name == 'VAT (Output VAT)') {
			// 			product.taxes_id[0] = product.pos.taxes[k].id
			// 		}
			// 	}
			// }
			console.log("product", product);
			console.log("product.taxes_id[0]", product.taxes_id[0]);
			// Add the product after having the extra information.
			await this.currentOrder.add_product(product, options);
			NumberBuffer.reset();
		}

	};
Registries.Component.extend(ProductScreen, clickProductScreen);


class DiscountPopup extends AbstractAwaitablePopup {
	constructor() {

		super(...arguments);
		this.state = useState({ discountData: { discount: 20 } });
		//useListener('click-product', this._clickProduct);
	}

	get currentOrder() {
		return this.env.pos.get_order();
	}

	captureVat(event) {
		if (event.target.value == 'vat_in') {
			document.getElementById('dicountValue').value = '5'
			this.state.discountData['discount'] = 5
		} else if (event.target.value == 'vat_ex') {
			document.getElementById('dicountValue').value = '20'
			this.state.discountData['discount'] = 20
		} else {
			document.getElementById('dicountValue').value = '0'
			this.state.discountData['discount'] = 0
		}
	}

	async applyConfirm() {
		// this is triggered when the apply button is pressed
		console.log("applyConfirm triggered");
		var discount = this.state.discountData['discount'];
		var selectedPartner = this.env.pos.get_order().get_client()

		// Fetch VAT Exempt Tax selected in config which will be applied in
		// VAT Exclusive Transactions.
		var selectedVATExemptTax = this.env.pos.config.vat_exempt_tax_config;
		//capture vat_selection_id
		var vat_selection_value = document.getElementById("vat_selection_id").value;

		if (vat_selection_value != ""){
			if (selectedPartner != null) {
				// check if selectedVATExemptTax is an array and not empty, if true: continue
				// else throw error
				if(!(!Array.isArray(selectedVATExemptTax) || !selectedVATExemptTax.length)){
					if (selectedPartner.check_sc_pwd && (selectedPartner.sc_id || selectedPartner.pwd_id)) {
						
						// Service Charge
						// Below two lines is added to calculate services charge amount.
						//.get_orderlines().filter(e => e.get_product() != product)
						//var product = this.env.pos.db.get_product_by_id(this.env.pos.config.service_product_id[0]);
						// Added by Janarthanan D
						
						var service_product = undefined
						if (this.env.pos.config.service_product_id) {
							service_product = this.env.pos.db.get_product_by_id(this.env.pos.config.service_product_id[0]);
						}
						
						_.each(this.env.pos.get_order().get_orderlines().filter(e => e.get_product() != service_product), function (orderline) {
							if (orderline) {
								console.log("orderline", orderline);
								/*changed the the tax type based on customer*/
								// check if its vat exclusive vs vat inclusive
								// if vat inclusive, do not change tax type to vat exempt
								// if vat exclusive, change tax type to vat exempt
								//		and price = pricewithouttax
		
								if(vat_selection_value == "vat_in") {
									console.log("VAT INCLUSIVE triggered");
									if (orderline.selected) {
										console.log("original tax_ids", orderline.tax_ids);
										//reset all discounts
										orderline.set_discount(0);
										orderline.is_vat_exclusive = false;
										orderline.pricelist_discount_amount = 0;

										orderline.set_discount(discount);

										//save discount as sc_discount / pwd_discount
										//reset is_sc_pressed/is_pwd_pressed
										if (orderline.is_sc_pressed) {
											orderline.sc_discount = discount;
										}
										else if (orderline.is_pwd_pressed) {
											orderline.pwd_discount = discount;
										}
										orderline.is_sc_pressed = false;
										orderline.is_pwd_pressed = false;
									}
								}
								else if (vat_selection_value == "vat_ex"){
									console.log("VAT EXCLUSIVE triggered");

									if (orderline.selected) {
										//reset discount and call reset functions
										orderline.set_discount(0);

										//get price_without_tax value before overwriting orderline.tax_ids
										var temp_price_without_tax = orderline.get_price_without_tax() / orderline.quantity;

										orderline.set_discount(discount);

										// Overwrite orderline.tax_ids as VAT - Exempt and do not change the
										// product.taxes_id. Since by changing the product.taxes_id,
										// the change will reflect to all orderlines that has the
										// same product. By overwriting orderline.tax_ids, this will
										// ensure that the changes in tax type will only reflect on 
										// that orderline.
										orderline.tax_ids = [selectedVATExemptTax[0]];
	
										//overwrite unit_price with temp_price_without_tax
										//check for pricelist
										//if pricelist, use new unit price to calculate without tax, overwrite unit price
										//else, overwrite unit price
										//if orderline.is_vat_exclusive = true, do not set unit price
										// if(orderline.is_vat_exclusive != true){
											//if orderline is not default, meaning there is an orderline selected
											if(orderline.pos.default_pricelist != orderline.order.pricelist){
												var price_unit = orderline.get_unit_price()
												var taxtotal = 0;

												var product =  orderline.get_product();
												var taxes_ids = product.taxes_id;
												taxes_ids = _.filter(taxes_ids, t => t in orderline.pos.taxes_by_id);
												var taxdetail = {};
												var product_taxes = orderline.get_taxes_after_fp(taxes_ids);

												var all_taxes = orderline.compute_all(product_taxes, price_unit, 1, orderline.pos.currency.rounding);
												_(all_taxes.taxes).each(function(tax) {
													taxtotal += tax.amount;
													taxdetail[tax.id] = tax.amount;
												});
												temp_price_without_tax = all_taxes.total_excluded;
												orderline.pricelist_discount_amount = (orderline.product.lst_price - price_unit) * orderline.quantity;
												
											}
											orderline.set_unit_price(temp_price_without_tax);
										// }
										//save discount as sc_discount/pwd_discount
										//reset is_sc_pressed/is_pwd_pressed
										if (orderline.is_sc_pressed) {
											orderline.sc_discount = discount;
										}
										else if (orderline.is_pwd_pressed) {
											orderline.pwd_discount = discount;
										}
										orderline.is_sc_pressed = false;
										orderline.is_pwd_pressed = false;

										//enable is_vat_exclusive
										orderline.is_vat_exclusive = true;
									}
								}							
							}
						});
						
						// Service Charge
						// Below line is added to calculate services charge amount.
						//this.env.pos.get_order()._update_service_amount()
						// Added by Janarthanan D
						
						if (service_product) {
							this.env.pos.get_order()._update_service_amount()
						}
						
		
						this.props.resolve({ confirmed: true });
						this.trigger('close-popup');
					} else {
							// TODO: redirect to customer records after popup.

					this.showPopup('ConfirmPopup', {
							title: this.env._t('Alert'),
							body: this.env._t('Selected customer has no SC/PWD ID.'),
						});
							
						// code snippet from ProductScreen.js
						const { confirmed, payload: newClient } = await this.showTempScreen(
							'ClientListScreen'
						);
						if (confirmed) {
							this.currentOrder.set_client(newClient);
							this.currentOrder.updatePricelist(newClient);
						}
				}
				} else {
					this.showPopup('ConfirmPopup', {
						title: this.env._t('Alert'),
						body: this.env._t('Please go back to the configuration of this POS and make sure that the VAT Exempt Tax is not blank.'),
					});
				}
			} else {
				// TODO: redirect to customer records after this popup.

				this.showPopup('ConfirmPopup', {
					title: this.env._t('Alert'),
					body: this.env._t('Please select the customer'),
				});

				// code snippet from ProductScreen.js
				const { confirmed, payload: newClient } = await this.showTempScreen(
					'ClientListScreen'
				);
				if (confirmed) {
					this.currentOrder.set_client(newClient);
					this.currentOrder.updatePricelist(newClient);
				}

			}
		}
		else {
			this.showPopup('ConfirmPopup', {
				title: this.env._t('Alert'),
				body: this.env._t('Please select if VAT inclusive or VAT exclusive'),
			});
		}
	}

	async confirm() {
		// this is triggered when the apply to all button is pressed
		console.log("confirm triggered");
		var discount = this.state.discountData['discount'];
		var selectedPartner = this.env.pos.get_order().get_client()
		
		// Fetch VAT Exempt Tax selected in config which will be applied in
		// VAT Exclusive Transactions.
		var selectedVATExemptTax = this.env.pos.config.vat_exempt_tax_config;
		//capture vat_selection_id
		var vat_selection_value = document.getElementById("vat_selection_id").value;

		if (vat_selection_value != ""){
			if (selectedPartner != null) {
				// check if selectedVATExemptTax is an array and not empty, if true: continue
				// else throw error
				if(!(!Array.isArray(selectedVATExemptTax) || !selectedVATExemptTax.length)){
					
					// Service Charge
						// Below two lines is added to calculate services charge amount.
						//.get_orderlines().filter(e => e.get_product() != product)
						//var product = this.env.pos.db.get_product_by_id(this.env.pos.config.service_product_id[0]);
						// Added by Janarthanan D
					
					var service_product = undefined
					if (this.env.pos.config.service_product_id) {
						service_product = this.env.pos.db.get_product_by_id(this.env.pos.config.service_product_id[0]);
					}
					
				
					if (selectedPartner.check_sc_pwd && (selectedPartner.sc_id || selectedPartner.pwd_id)) {
						_.each(this.env.pos.get_order().get_orderlines().filter(e => e.get_product() != service_product), function (orderline) {
							if (orderline) {
								console.log("orderline", orderline);
								/*changed the the tax type based on customer*/
								// check if its vat exclusive vs vat inclusive
								// if vat inclusive, do not change tax type to vat exempt
								// if vat exclusive, change tax type to vat exempt
								//		and price = pricewithouttax
		
								if(vat_selection_value == "vat_in") {
									console.log("VAT INCLUSIVE triggered");
									
									console.log("original tax_ids", orderline.tax_ids);
									//reset all discounts
									orderline.set_discount(0);
									orderline.is_vat_exclusive = false;
									orderline.pricelist_discount_amount = 0;
									
									orderline.set_discount(discount);

									//save discount as sc_discount/pwd_discount
									//reset is_sc_pressed/is_pwd_pressed
									if (orderline.is_sc_pressed) {
										orderline.sc_discount = discount;
									}
									else if (orderline.is_pwd_pressed) {
										orderline.pwd_discount = discount;
									}
									orderline.is_sc_pressed = false;
									orderline.is_pwd_pressed = false;
									
								}
								else if (vat_selection_value == "vat_ex"){
									console.log("VAT EXCLUSIVE triggered");
									//reset discount and call reset functions
									orderline.set_discount(0);

									//get price_without_tax value before overwriting orderline.tax_ids
									var temp_price_without_tax = orderline.get_price_without_tax() / orderline.quantity;

									orderline.set_discount(discount);

									// Overwrite orderline.tax_ids as VAT - Exempt and do not change the
									// product.taxes_id. Since by changing the product.taxes_id,
									// the change will reflect to all orderlines that has the
									// same product. By overwriting orderline.tax_ids, this will
									// ensure that the changes in tax type will only reflect on 
									// that orderline.
									orderline.tax_ids = [selectedVATExemptTax[0]];

									//overwrite unit_price with temp_price_without_tax
									//check for pricelist
									//if pricelist, use new unit price to calculate without tax, overwrite unit price
									//else, overwrite unit price
									//if orderline.is_vat_exclusive = true, do not set unit price
									// if(orderline.is_vat_exclusive != true){
										//if orderline is not default, meaning there is an orderline selected
										if(orderline.pos.default_pricelist != orderline.order.pricelist){
											var price_unit = orderline.get_unit_price()
											var taxtotal = 0;

											var product =  orderline.get_product();
											var taxes_ids = product.taxes_id;
											taxes_ids = _.filter(taxes_ids, t => t in orderline.pos.taxes_by_id);
											var taxdetail = {};
											var product_taxes = orderline.get_taxes_after_fp(taxes_ids);

											var all_taxes = orderline.compute_all(product_taxes, price_unit, 1, orderline.pos.currency.rounding);
											_(all_taxes.taxes).each(function(tax) {
												taxtotal += tax.amount;
												taxdetail[tax.id] = tax.amount;
											});
											temp_price_without_tax = all_taxes.total_excluded;
											orderline.pricelist_discount_amount = (orderline.product.lst_price - price_unit) * orderline.quantity;
											
										}

										orderline.set_unit_price(temp_price_without_tax);
									// }
									//save discount as sc_discount/pwd_discount
									//reset is_sc_pressed/is_pwd_pressed
									if (orderline.is_sc_pressed) {
										orderline.sc_discount = discount;
									}
									else if (orderline.is_pwd_pressed) {
										orderline.pwd_discount = discount;
									}
									orderline.is_sc_pressed = false;
									orderline.is_pwd_pressed = false;

									//enable is_vat_exclusive
									orderline.is_vat_exclusive = true;
									
								}							
							}
						});
						
						// Service Charge
						// Below line is added to calculate services charge amount.
						// this.env.pos.get_order()._update_service_amount()
						// Added by Janarthanan D
						
						if (service_product) {
							this.env.pos.get_order()._update_service_amount()
						}
		
						this.props.resolve({ confirmed: true });
						this.trigger('close-popup');
					} else {
						this.showPopup('ConfirmPopup', {
							title: this.env._t('Alert'),
							body: this.env._t('Selected customer has no SC/PWD.'),
						});
						// code snippet from ProductScreen.js
						const { confirmed, payload: newClient } = await this.showTempScreen(
							'ClientListScreen'
						);
						if (confirmed) {
							this.currentOrder.set_client(newClient);
							this.currentOrder.updatePricelist(newClient);
						}
					}
				} else {
					this.showPopup('ConfirmPopup', {
						title: this.env._t('Alert'),
						body: this.env._t('Please go back to the configuration of this POS and make sure that the VAT Exempt Tax is not blank.'),
					});
				}
			} else {
				this.showPopup('ConfirmPopup', {
					title: this.env._t('Alert'),
					body: this.env._t('Please select the customer'),
				});
				// code snippet from ProductScreen.js
				const { confirmed, payload: newClient } = await this.showTempScreen(
					'ClientListScreen'
				);
				if (confirmed) {
					this.currentOrder.set_client(newClient);
					this.currentOrder.updatePricelist(newClient);
				}
			}
		}
		else {
			this.showPopup('ConfirmPopup', {
				title: this.env._t('Alert'),
				body: this.env._t('Please select if VAT inclusive or VAT exclusive'),
			});
		}
	}
	captureChange(event) {
		this.state.discountData[event.target.name] = event.target.value;
	}
}
//Create products popup
DiscountPopup.template = 'DiscountPopup';
DiscountPopup.defaultProps = {
	confirmText: 'Ok',
	cancelText: 'Cancel',
	title: 'Discount',
	body: '',
};
Registries.Component.add(DiscountPopup);
//   return DiscountPopup;
export default DiscountPopup;
