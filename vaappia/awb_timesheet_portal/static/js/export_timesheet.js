odoo.define('awb_timesheet_portal.export_timesheet', function(require){
    'use strict';
    
    var Animation = require('website.content.snippets.animation');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');
   /* var registry = require('web.field_registry');
    //import { registry } from "@web/core/registry";
    import framework from 'web.framework';
    import session from 'web.session';*/
    
   





		 
	
/*registry.category("ir.actions.report handlers").add("xlsx", async (action) => {
	if (action.report_type === 'xlsx') {
    	framework.blockUI();
    	var def = $.Deferred();
    	session.get_file({
        	url: '/xlsx_reports',
        	data: action.data,
        	success: def.resolve.bind(def),
        	error: (error) => this.call('crash_manager', 'rpc_error', error),
        	complete: framework.unblockUI,
    	});
    	return def;
	}
	});
})



/*
	$('.export_div').click(function(){
	 let $cbs = {};
		alert("New alerttt")
		$cbs = $('input[name="check"]').click(function() {
			ajax.jsonRpc("/usecheck/records", 'call',{}).then(function(result){
       if (result['employee'] === "true"){
        $edit.toggle( $cbs.is(":checked") );

       }
       else{
       $export.toggle( $cbs.is(":checked") );

       }


  });
		alert("check clickedd")
		 
	});
	});*/
	
	
	
	//Export Button Functioanlity
	
	$('.edit_button_class').on('click','.Export',function(){
		
		

var checkBoxes = document.getElementsByName('check');
var checkboxesChecked = [];
  for (var i=0; i<checkBoxes.length; i++) {
     if (checkBoxes[i].checked) {
        checkboxesChecked.push(checkBoxes[i].id);
     }
  }
  ajax.post("/export/timesheets/records", //'call',
  {'checked':checkboxesChecked}).then(function(result)
  
  {

  //alert(result['result'])
// (C1) DUMMY DATA


	var data = [["Date", "Employee", "Project", "Task", "Description", "Hours", "Project Type", "Activity Type", "Platform", "status"] ];
	
	 var s = result; //" [{'id':1,'name':'Test1'},{'id':2,'name':'Test2'},{'id':3,'name':'Test3'},{'id':4,'name':'Test4'}]";
	 var myObject = eval('(' + s + ')');
		for (i in myObject)
		{
			var vals = []
		    vals.push(myObject[i]["date"],myObject[i]["employee"],myObject[i]["project"],myObject[i]["task"],myObject[i]["description"],myObject[i]["hours"],myObject[i]["project_type"],myObject[i]["activity_type"],myObject[i]["platform"],myObject[i]["status"]);
			data.push(vals)
		}
	// (C2) CREATE NEW EXCEL "FILE"
	var workbook = XLSX.utils.book_new(),
	    worksheet = XLSX.utils.aoa_to_sheet(data);
	workbook.SheetNames.push("First");
	workbook.Sheets["First"] = worksheet;
	
	// (C3) "FORCE DOWNLOAD" XLSX FILE
	XLSX.writeFile(workbook, "Timesheets.xlsx");
  });
  
    /* ajax.post('/shop/cart/update_option', {})
                    .then(function (quantity) {
                        if (goToShop) {
                            window.location.pathname = "/shop/cart";
                        }
                        const $quantity = $(".my_cart_quantity");
                        $quantity.parent().parent().removeClass('d-none');
                        $quantity.text(quantity).hide().fadeIn(600);
                    });*/
                    
           
  
});
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
});