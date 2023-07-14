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

			await this.currentOrder.add_product(product, options);
			NumberBuffer.reset();
		}

	};
Registries.Component.extend(ProductScreen, clickProductScreen);


class DiscountPopupSP extends AbstractAwaitablePopup {
	constructor() {

		super(...arguments);
		this.state = useState({ discountData: { discount: 10 } });
		//useListener('click-product', this._clickProduct);
	}

	get currentOrder() {
		return this.env.pos.get_order();
	}

	captureVat(event) {
		document.getElementById('dicountValue').value = '10'
		this.state.discountData['discount'] = 10
	}

	async applyConfirm() {
		// this is triggered when the apply button is pressed
		// console.log("applyConfirm triggered");
		var discount = this.state.discountData['discount'];
		var selectedPartner = this.env.pos.get_order().get_client()

		//capture vat_selection_id
		var vat_selection_value = document.getElementById("vat_selection_id").value;

		if (vat_selection_value != "") {
			if (selectedPartner != null) {
				if (selectedPartner.check_sc_pwd) {
					_.each(this.env.pos.get_order().get_orderlines(), function (orderline) {
						if (orderline) {
							// console.log("orderline", orderline);
							/*changed the the tax type based on customer*/
							// check if its vat exclusive vs vat inclusive
							// if vat inclusive, do not change tax type to vat exempt
							// if vat exclusive, change tax type to vat exempt
							//		and price = pricewithouttax

							if (vat_selection_value == "vat_ex") {

								for (let k = 0; k < orderline.pos.taxes.length; k++) {
									// console.log("for loop trigger", k);
									if (orderline.pos.taxes[k].name == 'VAT - Exempt') {
										// console.log("VAT - Exempt is true", k, orderline.selected);
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
											orderline.tax_ids = [orderline.pos.taxes[k].id];

											//overwrite unit_price with temp_price_without_tax
											//check for pricelist
											//if pricelist, use new unit price to calculate without tax, overwrite unit price
											//else, overwrite unit price
											//if orderline.is_vat_exclusive = true, do not set unit price
											if (orderline.is_vat_exclusive != true) {
												//if orderline is not default, meaning there is an orderline selected
												if (orderline.pos.default_pricelist != orderline.order.pricelist) {
													var price_unit = orderline.get_unit_price()
													var taxtotal = 0;

													var product = orderline.get_product();
													var taxes_ids = product.taxes_id;
													taxes_ids = _.filter(taxes_ids, t => t in orderline.pos.taxes_by_id);
													var taxdetail = {};
													var product_taxes = orderline.get_taxes_after_fp(taxes_ids);

													var all_taxes = orderline.compute_all(product_taxes, price_unit, 1, orderline.pos.currency.rounding);
													_(all_taxes.taxes).each(function (tax) {
														taxtotal += tax.amount;
														taxdetail[tax.id] = tax.amount;
													});
													temp_price_without_tax = all_taxes.total_excluded;
													orderline.pricelist_discount_amount = (orderline.product.lst_price - price_unit) * orderline.quantity;

												}
												orderline.set_unit_price(temp_price_without_tax);
											}

											if (orderline.is_sp_pressed) {
												orderline.sp_discount = discount;
											}

											orderline.is_sp_pressed = false;
											//enable is_vat_exclusive
											orderline.is_vat_exclusive = true;
										}
									}
								}
							}
						}
					});

					this.props.resolve({ confirmed: true });
					this.trigger('close-popup');
				} else {
					this.showPopup('ConfirmPopup', {
						title: this.env._t('Alert'),
						body: this.env._t('Selected customer has no SC/PWD/Solo-Parent.'),
					});
				}
			} else {
				this.showPopup('ConfirmPopup', {
					title: this.env._t('Alert'),
					body: this.env._t('Please select the customer'),
				});
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
		// console.log("confirm triggered");
		var discount = this.state.discountData['discount'];
		var selectedPartner = this.env.pos.get_order().get_client()

		//capture vat_selection_id
		var vat_selection_value = document.getElementById("vat_selection_id").value;

		if (vat_selection_value != "") {
			if (selectedPartner != null) {
				if (selectedPartner.check_sc_pwd) {
					_.each(this.env.pos.get_order().get_orderlines(), function (orderline) {
						if (orderline) {
							// console.log("orderline", orderline);
							/*changed the the tax type based on customer*/
							// check if its vat exclusive vs vat inclusive
							// if vat inclusive, do not change tax type to vat exempt
							// if vat exclusive, change tax type to vat exempt
							//		and price = pricewithouttax
							if (vat_selection_value == "vat_ex") {
								// console.log("VAT EXCLUSIVE triggered");
								for (let k = 0; k < orderline.pos.taxes.length; k++) {
									// console.log("for loop trigger", k);
									if (orderline.pos.taxes[k].name == 'VAT - Exempt') {
										// console.log("VAT - Exempt is true", k);
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
										orderline.tax_ids = [orderline.pos.taxes[k].id];

										//overwrite unit_price with temp_price_without_tax
										//check for pricelist
										//if pricelist, use new unit price to calculate without tax, overwrite unit price
										//else, overwrite unit price
										//if orderline.is_vat_exclusive = true, do not set unit price
										if (orderline.is_vat_exclusive != true) {
											//if orderline is not default, meaning there is an orderline selected
											if (orderline.pos.default_pricelist != orderline.order.pricelist) {
												var price_unit = orderline.get_unit_price()
												var taxtotal = 0;

												var product = orderline.get_product();
												var taxes_ids = product.taxes_id;
												taxes_ids = _.filter(taxes_ids, t => t in orderline.pos.taxes_by_id);
												var taxdetail = {};
												var product_taxes = orderline.get_taxes_after_fp(taxes_ids);

												var all_taxes = orderline.compute_all(product_taxes, price_unit, 1, orderline.pos.currency.rounding);
												_(all_taxes.taxes).each(function (tax) {
													taxtotal += tax.amount;
													taxdetail[tax.id] = tax.amount;
												});
												temp_price_without_tax = all_taxes.total_excluded;
												orderline.pricelist_discount_amount = (orderline.product.lst_price - price_unit) * orderline.quantity;

											}
											orderline.set_unit_price(temp_price_without_tax);
										}

										if (orderline.is_sp_pressed) {
											orderline.sp_discount = discount;
										}

										orderline.is_sp_pressed = false;
										//enable is_vat_exclusive
										orderline.is_vat_exclusive = true;

									}
								}

							}
						}
					});

					this.props.resolve({ confirmed: true });
					this.trigger('close-popup');
				} else {
					this.showPopup('ConfirmPopup', {
						title: this.env._t('Alert'),
						body: this.env._t('Selected customer has no SC/PWD/Solo-Parent.'),
					});
				}
			} else {
				this.showPopup('ConfirmPopup', {
					title: this.env._t('Alert'),
					body: this.env._t('Please select the customer'),
				});
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
DiscountPopupSP.template = 'DiscountPopupSP';
DiscountPopupSP.defaultProps = {
	confirmText: 'Ok',
	cancelText: 'Cancel',
	title: 'Discount',
	body: '',
};
Registries.Component.add(DiscountPopupSP);
//   return DiscountPopupSP;
export default DiscountPopupSP;
