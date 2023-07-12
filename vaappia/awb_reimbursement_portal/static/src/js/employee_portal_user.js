odoo.define('awb_reimbursement_portal.employee_portal_user', function (require) {
	'use strict';
	var ajax = require('web.ajax');
	// Check box action
	$(document).ready(function() {
		var $submit = $(".submit_class").hide()
			var $cbs = $('input[name="check_box"]').click(function() {
				$submit.toggle($cbs.is(":checked"))
			});
	});
	// Create button action
	$(document).ready(function() {
		$('#mydiv_expense').on('click', '.my_div_expense', function() {
//			Clear Form
			$('#product').find('option').remove().end().append('<option value=""></option>');
			$('#taxes').find('option').remove().end().append('<option value=""></option>');
			ajax.jsonRpc("/create/expenses/records", 'call', {

			}).then(function(result) {
				var product = result['product']
				var ProductSelect = document.getElementById('product');
				for (let i = 0; i < product.length; i++) {
					var item = document.createElement('option');
					item.text = product[i].name
					item.id = product[i].id
					item.value = product[i].id
					ProductSelect.appendChild(item);
				}
				var taxes = result['taxes']
				var TaxesSelect = document.getElementById('taxes');
				for (let i = 0; i < taxes.length; i++) {
					var item = document.createElement('option');
					item.text = taxes[i].name
					item.id = taxes[i].id
					item.value = taxes[i].id
					TaxesSelect.appendChild(item);
				}
				var account = result['account']
				var AccountSelect = document.getElementById('account');
				for (let i = 0; i < account.length; i++) {
					var item = document.createElement('option');
					item.text = account[i].name
					item.id = account[i].id
					item.value = account[i].id
					AccountSelect.appendChild(item);
				}
				var employee = result['employee']
				var EmployeeSelect = document.getElementById('employee');
				for (let i = 0; i < employee.length; i++) {
					var item = document.createElement('option');
					item.text = employee[i].name
					item.id = employee[i].id
					item.value = employee[i].id
					EmployeeSelect.appendChild(item);
				}
				var analytic_act = result['analytic_act']
				var AnalyticSelect = document.getElementById('analytic_act');
				for (let i = 0; i < analytic_act.length; i++) {
					var item = document.createElement('option');
					item.text = analytic_act[i].name
					item.id = analytic_act[i].id
					item.value = analytic_act[i].id
					AnalyticSelect.appendChild(item);
				}
				var analytic_tag = result['analytic_tag']
				var AnalyticTagSelect = document.getElementById('analytic_tag');
				for (let i = 0; i < analytic_tag.length; i++) {
					var item = document.createElement('option');
					item.text = analytic_tag[i].name
					item.id = analytic_tag[i].id
					item.value = analytic_tag[i].id
					AnalyticTagSelect.appendChild(item);
				}

				$("#date_start").datepicker({
					changeMonth: true,
					changeYear: true,
					dateFormat: "yy-mm-dd"
				});
				
			});

		});
		// Submit button action
		$('.submit_class').on('click', function(){
			var checkboxes = document.getElementsByName('check_box');
	    	var checkboxesChecked = [];
	    	  for (var i=0; i<checkboxes.length; i++) {
	    	     if (checkboxes[i].checked) {
	    	        checkboxesChecked.push(checkboxes[i].id);
	    	     }
	    	  }
	    	  $('input:checked').not('.all').parents("tr").remove();
	    	 ajax.jsonRpc("/submit/expenses", 'call',{'checked':checkboxesChecked}).then(function(modal){
	    		 $('.expense_lines_ids tr#empty_lines').before(modal);
	    		  }).then(function(modal) {
	    				window.location.reload();
	    			});
		});
	});	
	
});