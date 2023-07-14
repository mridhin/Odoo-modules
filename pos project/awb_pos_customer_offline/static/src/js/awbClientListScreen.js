odoo.define('awb_pos_customer_offline.awbClientListScreen', function (require) {
"use strict";
	
	const ClientListScreen = require('point_of_sale.ClientListScreen')
	const Registries = require('point_of_sale.Registries');
	const { isConnectionError } = require('point_of_sale.utils');
	
	


	/*Extended clientListScreen to implement offline customer functions*/
	const awbClientListScreen = (ClientListScreen) =>
        class extends ClientListScreen {
            constructor() {
                super(...arguments);
            }
        	
        	/*Creating a customer dict and appended in partner_by_id db. And rendered in client screen*/
        	get clients() {
	            let res;
	            if (this.env.pos.config.awb_customer_offline) {
					if (this.state.query && this.state.query.trim() !== '') {
		                res = this.env.pos.db.search_partner(this.state.query.trim());
		            } else {
						
		                res = this.env.pos.db.get_partners_sorted(1000);
		            }
		            
		            
		            var result =  res.sort(function (a, b) { return (a.name || '').localeCompare(b.name || '') });
					var newClients = []
					var offline = this.env.pos.db.posCustomerOfflineDup
					
					for (let i = 0; i < offline.length; i++) {
						var country = []
						var state = []
						var pricelist = []
						//console.log(offline[i]['country_id'])
						for (let j = 0; j < this.env.pos.countries.length; j++) {
							//console.log(this.env.pos.countries[j].id)
							if (this.env.pos.countries[j].id == offline[i]['country_id']) {
								
								country.push(this.env.pos.countries[j].id, this.env.pos.countries[j].name)
								}
						}
						for (let k = 0; k < this.env.pos.states.length; k++) {
							if (this.env.pos.states[k].id == offline[i]['state_id']) {
								state.push(this.env.pos.states[k].id, this.env.pos.states[k].name)
							}
						}
						for (let l = 0; l < this.env.pos.pricelists.length; l++) {
							if (this.env.pos.pricelists[l].id == offline[i]['property_product_pricelist']) {
								pricelist.push(this.env.pos.pricelists[l].id, this.env.pos.pricelists[l].display_name)
							}
						}
						var copyCli = {}
						var address = offline[i].street +", "+ offline[i].zip +", "+ offline[i].city +", " +state[1]+", " +country[1]
						
						copyCli['id'] = offline[i].id
						copyCli['name'] = offline[i].name
						copyCli['street'] = offline[i].street
						copyCli['city'] = offline[i].city
						copyCli['state_id'] = state
						copyCli['email'] = offline[i].email
						
						
						copyCli['zip'] = offline[i].zip
						copyCli['address'] = address
						copyCli['total_due'] = 0
						copyCli['barcode'] = offline[i].barcode || false
						copyCli['check_sc_pwd'] = false
						
						copyCli['lang'] = offline[i].lang || 'en_US'
						copyCli['phone'] = offline[i].phone || ''
						copyCli['mobile'] = false
						copyCli['property_account_position_id'] = false
						copyCli['sh_customer_discount'] = 0
						copyCli['vat'] = false
						copyCli['loyalty_points'] = offline[i].id
						copyCli['property_product_pricelist'] = offline[i].id
						copyCli['country_id'] = country
						
						
						newClients.push(copyCli)
					} 
					
					if( (newClients.length) > 0) {
						
						
						for (let c = 0; c < newClients.length; c++) {
							result.push(newClients[c])
							this.env.pos.db.partner_sorted.push(newClients[c].id)
							this.env.pos.db.partner_by_id[newClients[c].id] = newClients[c]
							
						}
						
						this.env.pos.db.posCustomerOfflineDup = []
						return result
					} else {
						
						return result
					}
					
				} else {
		            if (this.state.query && this.state.query.trim() !== '') {
		                res = this.env.pos.db.search_partner(this.state.query.trim());
		            } else {
		                res = this.env.pos.db.get_partners_sorted(1000);
		            }
		            return res.sort(function (a, b) { return (a.name || '').localeCompare(b.name || '') });
	        	}
	        }
        	
        	/*override base save changes function and to check the whether it's offline creation or not and proceed changes*/
        	async saveChanges(event) {
				var self = this
				var clientValues = Object.keys(this.env.pos.db.partner_by_id);
	            
	            if (event.detail.processedChanges['id']) {
					var contentBody = 'Details Saved'
				} else {
					var contentBody = 'Customer Created'
				}
	             
	            try {
	                let partnerId = await this.rpc({
	                    model: 'res.partner',
	                    method: 'create_from_ui',
	                    args: [event.detail.processedChanges],
	                });
	                await this.env.pos.load_new_partners();
	                this.state.selectedClient = this.env.pos.db.get_partner_by_id(partnerId);
	                this.state.detailIsShown = false;
	                this.render();
	            } catch (error) {
	                if (isConnectionError(error)) {
						
						if (this.env.pos.config.awb_customer_offline) {
							const { confirmed, payload } = await this.showPopup('ConfirmPopup', {
		                        title: this.env._t('Customer'),
		                        body: this.env._t(contentBody),
		                        confirmed: true,
		                    }); 
		                    
			                if (confirmed) {
								if (event.detail.processedChanges['id']) {
									var offlineEdit = this.env.pos.db.posCustomerOffline
									for (let i = 0; i < offlineEdit.length; i++) {
										if(offlineEdit[i].id == event.detail.processedChanges['id']) {
											let keys = Object.keys(event.detail.processedChanges) ;
											for (let j = 0; j < keys.length; j++) {
												offlineEdit[i][keys[j]] = event.detail.processedChanges[keys[j]]
												
											}
											
										}
									}
									/*Need to check on the partner by id function.*/
									var partnerByEdit = []
									partnerByEdit.push(this.env.pos.db.get_partner_by_id(event.detail.processedChanges['id']))
									
									
									for (let k = 0; k < partnerByEdit.length; k++) {
										if(partnerByEdit[k].id == event.detail.processedChanges['id']) {
											let keys = Object.keys(event.detail.processedChanges) ;
											
											for (let j = 0; j < keys.length; j++) {
												var country = []
												var state = []
												if (keys[j] == 'country_id') {
													for (let c = 0; c < this.env.pos.countries.length; c++) {
														if (this.env.pos.countries[c].id == event.detail.processedChanges[keys[j]]) {
															country.push(this.env.pos.countries[c].id, this.env.pos.countries[c].name)
															partnerByEdit[k][keys[j]] = country
														}
													}
												} else if (keys[j] == 'state_id') {
													for (let s = 0; s < this.env.pos.states.length; s++) {
														if (this.env.pos.states[s].id == event.detail.processedChanges[keys[j]]) {
															state.push(this.env.pos.states[s].id, this.env.pos.states[s].name)
															partnerByEdit[k][keys[j]] = state
														}
													}

												} else {
													partnerByEdit[k][keys[j]] = event.detail.processedChanges[keys[j]]
												}
												var st = event.detail.processedChanges['street'] || partnerByEdit[k].street
												var zp = event.detail.processedChanges['zip'] || partnerByEdit[k].zip
												var cy = event.detail.processedChanges['city'] || partnerByEdit[k].city
												var sat = state[1] || partnerByEdit[k].state_id[1]
												var cot = state[1] || partnerByEdit[k].country_id[1]
												partnerByEdit[k]['address'] = st + ", " + zp + ", " + cy + ", " + sat + ", " + cot
											}
										}
									}
									$('.back').click();
								} else {
					                	var partner = Math.max(...clientValues.map(Number))
					                	var offPartner = this.env.pos.db.posCustomerOfflineDup.length
					                	var newId = partner + offPartner + 1
						                event.detail.processedChanges['id'] = newId
						                self.env.pos.db.setPosCustomerOffline(event.detail.processedChanges)
										self.env.pos.db.setPosCustomerOfflineDup(event.detail.processedChanges)
								        $('.back').click();
						        }
							}
						} else {
		                    await this.showPopup('OfflineErrorPopup', {
		                        title: this.env._t('Offline'),
		                        body: this.env._t('Unable to save changes.'),
		                    }); 
	                    }
	                } else {
	                    throw error;
	                }
	            }
	        }
        }
	Registries.Component.extend(ClientListScreen, awbClientListScreen)

});