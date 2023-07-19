odoo.define('awb_hr_timesheet.timesheet', function(require) {
	'use strict';

	var Animation = require('website.content.snippets.animation');
	var ajax = require('web.ajax');
	var Widget = require('web.Widget');
	var publicWidget = require('web.public.widget');
	var core = require('web.core');
	var QWeb = core.qweb;
	var rpc = require('web.rpc');
	var _t = core._t;

	$(document).ready(function() {
		// Added class name
		var current_url = window.location;
		if (current_url.pathname == '/my/timesheets'){
			self.$('.mb64').addClass('timesheet_width');
			}
		$("table tr.thead-light th:nth-child(2)").attr('colspan', 8);

		ajax.jsonRpc("/usecheck/records", 'call', {

		}).then(function(result) {
		    try {
		        if (result['employee'] != "true") {
                    var x = document.querySelectorAll("#reject_button2");
                    for (let i = 0; i < x.length; i++) {
                        x[i].style.display = "block";
                    }
                    document.getElementById("reject_button1").style.display = "block";
                }
		    } catch (err) {
		        console.log('Logged in user has no employee assigned.')
		    }

		});

		$('#mydiv').on('click', '.my_div', function() {
//			Clear Form
			$('#project').find('option').remove().end().append('<option value=""></option>');
			$('#activity').find('option').remove().end().append('<option value=""></option>');
			$('#project_type').find('option').remove().end().append('<option value=""></option>');
			$('#client').find('option').remove().end().append('<option value=""></option>');
			
			ajax.jsonRpc("/create/timesheets/records", 'call', {

			}).then(function(result) {
				//Get Current url value
				var current_url = window.location.search;
				$('#url').val(current_url)
				var employee = result['employee_rec']
				$('#employee-name').val(employee.name)
				$('#employee-id').val(employee.id)

				var client = result['partner']
				var project = result['project']
				var ProjectSelect = document.getElementById('project');
				for (let i = 0; i < project.length; i++) {
					var item = document.createElement('option');
					item.text = project[i].name
					item.id = project[i].id
					item.value = project[i].id
					ProjectSelect.appendChild(item);
				}

				var tag = result['tag']
				$("#date_start").datepicker({
					changeMonth: true,
					changeYear: true,
					dateFormat: "yy-mm-dd"
				});
			});

		});

		$('#activity').on('change', function(){
            ajax.jsonRpc("/get/project/activity/id", 'call', {
                'activity_id' : $(this).val(),
            })
            .then(function(data) {
                var activity = data['activity_type_rec']
                if(activity.name) {
                    $('.activity_type').val(activity.id)
			        $('#activity-type').val(activity.name)
                }

            });
		});

		$('#project').on('change', function(){
		    $('#activity').find('option').remove().end().append('<option value=""></option>');
            ajax.jsonRpc("/get/employee/project/id", 'call', {
                'project_id' : $(this).val(),
            })
            .then(function (data) {
                var company = data['company_rec']
                var activity = data['project_activity']
                $('#client-name').val(company.name)
			    $('#client-id').val(company.id)
			    var project = data['project_rec']
			    $('.project_type').val(project.type)
				$.each(activity, function (i, item) {
                    $('#activity').append($('<option>', {
                        value: item.id,
                        text : item.name
                    }));
                });
            });
		});
	});
	$(document).ready(function() {
		var $submit = $(".button_class").hide()
		var $edit = $(".edit_button_class").hide(),
			$cbs = $('input[name="check"]').click(function() {
				ajax.jsonRpc("/usecheck/records", 'call', {}).then(function(result) {
					if (result['employee'] === "true") {
						$edit.toggle($cbs.is(":checked"));
					} else {
						$submit.toggle($cbs.is(":checked"));
					}
				});
			});
	});

    $(".checkbox").click(function(){
		var total = 0
		var checkboxes = document.getElementsByName('check');
		var checkboxesChecked = [];
		for (var i = 0; i < checkboxes.length; i++) {
			if (checkboxes[i].checked) {
			checkboxesChecked.push(checkboxes[i].id);
			}
		}
		ajax.jsonRpc("/time/total", 'call', {
			'checked': checkboxesChecked
		}).then(function(result) {
			document.getElementById("selected_hours").innerHTML = result['total']
			if (result['result'] == 'false'){
			let user_input = confirm("Timesheet selection crosses another week,Do you want to continue?");
			console.log('input',user_input)
			if (user_input == true){
			for (var i = 0; i < checkboxesChecked.length; i++) {
			document.getElementById(checkboxesChecked[i]).checked = false;
			}

			document.getElementById(result['check_id']).checked = true;
			document.getElementById("selected_hours").innerHTML = result['new_hour']
			}
			else{
			console.log('check',document.getElementById(result['check_id']))
            document.getElementById(result['check_id']).checked = false;
			}
			}
		});
	});


	$('.button_class').on('click', '.approve', function() {
		var checkboxes = document.getElementsByName('check');
		var checkboxesChecked = [];
		for (var i = 0; i < checkboxes.length; i++) {

			if (checkboxes[i].checked) {
				checkboxesChecked.push(checkboxes[i].id);
			}
		}
		ajax.jsonRpc("/approve/timesheets/records", 'call', {
			'checked': checkboxesChecked
		}).then(function(result) {
			window.location.reload();
		});
	});

	$('.button_class').on('click', '.reject', function() {
		var checkboxes = document.getElementsByName('check');
		var checkboxesChecked = [];
		for (var i = 0; i < checkboxes.length; i++) {
			if (checkboxes[i].checked) {
				checkboxesChecked.push(checkboxes[i].id);
			}
		}
		ajax.jsonRpc("/reject/timesheets/records", 'call', {
			'checked': checkboxesChecked
		}).then(function(result) {
			if (result['result'] === "true") {
				window.location.reload();
			} else {
				alert("The timesheet is already validated");
				window.location.reload();
				return false;
			}

		});
	});

	$('.edit_button_class').on('click', '.delete', function() {
		var checkboxes = document.getElementsByName('check');
		var checkboxesChecked = [];
		for (var i = 0; i < checkboxes.length; i++) {
			if (checkboxes[i].checked) {
				checkboxesChecked.push(checkboxes[i].id);
			}
		}
		ajax.jsonRpc("/delete/timesheets/records", 'call', {
			'checked': checkboxesChecked
		}).then(function(result) {
			if (result['result'] === "true") {
				window.location.reload();
			} else {
				alert("You can delete timesheet only in draft state");
				window.location.reload();
				return false;
			}

		});
	});

	$('.edit_button_class').on('click', '.submit', function() {
		var checkboxes = document.getElementsByName('check');
		var checkboxesChecked = [];
		for (var i = 0; i < checkboxes.length; i++) {
			if (checkboxes[i].checked) {
				checkboxesChecked.push(checkboxes[i].id);
			}
		}
		ajax.jsonRpc("/submit/timesheets/records", 'call', {
			'checked': checkboxesChecked
		}).then(function(result) {
			if (result['result'] != "true") {
				alert("Please submit atleast 40 hours of draft timesheet");
				window.location.reload();
				return false;
			} else {
				window.location.reload();
			}
		});
	});

	$('.edit_button_class').on('click', '#edit', function() {
		var checkboxes = document.getElementsByName('check');

		var checkboxesChecked = [];
		for (var i = 0; i < checkboxes.length; i++) {
			if (checkboxes[i].checked) {
				if (checkboxes[i].title != 'draft') {
					$("#edit").removeAttr("disabled");

					alert("You can edit/update timeheet only in draft state");
					window.location.reload();
					return false;
				}
				checkboxesChecked.push(checkboxes[i].id);
			}
		}
		if (checkboxesChecked.length > 1) {
			$("#edit").removeAttr("disabled");
			return false;
		}
		ajax.jsonRpc("/edit/timesheets/records", 'call', {
			'checked': checkboxesChecked
		}).then(function(result) {

			$("#date").datepicker({
				changeMonth: true,
				changeYear: true,
				dateFormat: "yy-mm-dd"
			});
			document.getElementById("name").value = result['timesheet'][0].name;
			document.getElementById("timesheet_id").value = result['timesheet'][0].id;
			document.getElementById("date").value = result['timesheet'][0].date;
			document.getElementById("hours").value = result['timesheet'][0].hours;
			//Get Current url value
			var currentUrl = window.location.search;
			$('#url_name').val(currentUrl)

		});
	});

	$(".rejectButton").click(function() {
		var $item = $(this).closest("tr") // Finds the closest row <tr>
			.find(".reject_button2");
		document.getElementById("reject_timesheet_id").value = $item[0].title;

	});

	function validateFormcreate() {
		let x = document.forms["formtime"]["hours"].value;
		if (x > 24) {
			alert("Not allowed to enter more than 24 hours");
			return false;
		}

	}
	$("#warranty_submit").click(function(e) {
		let x = document.forms["formtime"]["hours"].value;
		let y = document.forms["formtime"]["date"].value;

		if (x > 24) {
			alert("Not allowed to enter more than 24 hours");
			return false;
		}

		ajax.jsonRpc("/check/date/records", 'call', {
			'date': y
		}).then(function(result) {

			if (result['timesheet'] === "true") {

				alert("Duplicate Record Exist");


			}

		});
	});

	$("#edit_submit").click(function(e) {
		let x = document.forms["formedit"]["hours"].value;
		let y = document.forms["formedit"]["date"].value;
		let z = document.forms["formedit"]["timesheet"].value;

		if (x > 24) {
			alert("Not allowed to enter more than 24 hours");
			return false;
		}

		ajax.jsonRpc("/check/update/date/records", 'call', {
			'date': y,
			'id':z
		}).then(function(result) {

			if (result['timesheet'] === "true") {

				alert("Duplicate Record Exist");


			}

		});
	});

});