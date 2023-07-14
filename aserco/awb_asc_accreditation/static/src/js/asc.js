odoo.define('awb_asc_accreditation.asc', function (require) {
    'use strict';
const buttons = document.querySelectorAll('.form_button')
const formPages = document.querySelectorAll('.form-page')
const bars = document.querySelectorAll('.bar-circle')

let pageStates = {
    oldPageNum: null,
    currentPage: null,
}

const pageTransform = () => {
    var vw  = $(document).width();
    if (vw < 768){
        if (pageStates.currentPage == 1){
            formPages[1].style.display = 'block'
        }else{
            formPages[1].style.display = 'none'
        }
        formPages.forEach(page => {
            if (page.id === 'final_message'){
                page.style.transform = `translateX(-${(pageStates.currentPage) * 50}%)`
            }else{
                page.style.transform = `translateX(-${(pageStates.currentPage) * 100}%)`
            }
        })
    }else{
        formPages.forEach(page => {
            page.style.transform = `translateX(-${(pageStates.currentPage) * 100}%)`
        })
    }
}

const handleClasses = () => {

    bars.forEach(bar => {
        bar.classList.remove('active')
    })

    if(pageStates.currentPage < 2) {
        bars[pageStates.currentPage].classList.add('active')
    }
    else{
        bars.forEach(bar => {
        bar.style.display = "none"
    })
    }
}

const indexFinder = (el) => {
    let i = 0;
    for(; el = el.previousElementSibling; i++);
    return i;
}

const pageHandler = (e) => {
    const navData = e.target.id
    
    if(navData == "proceed") {
    	var return_val = validatefirstpage();
    	if (!return_val) {
    		return false;
    	}
    }
    if(navData == "join_now") {
    	var value = validatesecondpage();
    	if (value === 'false') {
    		e.preventDefault()
    		return false;
    	}
    }


    if(navData == "back") {
        pageStates.currentPage = pageStates.currentPage - 1
    } else {
        pageStates.currentPage = pageStates.currentPage + 1
    }

    pageTransform()
    handleClasses()
}

buttons.forEach(button => {
    button.addEventListener('click', pageHandler)
})

// Created a one dummy file for the service and products

$(document).ready (function () {
    $("#sec_article_of_incorporation").hide();

	$(".team_user_ids").chosen({
	
		 enable_search_threshold : 10
		});
		
		$('#team_user_ids').change (function () {
		var UserIds = $('#team_user_ids').val();
		var ser_var=$('#existing_value').val(UserIds);
    });
    
    	$(".prod_team_user_ids").chosen({
	
		 enable_search_threshold : 10
		});
		
		$('#prod_team_user_ids').change (function () {
		var UserIds = $('#prod_team_user_ids').val();
		var prod_var=$('#prod_existing_value').val(UserIds);
    });

    $('.radio-custom').change(function(){
        $(".attachment_input").attr('disabled', false);
        var asc_type = $("input[type='radio'][name='asc_type']:checked").val();
        if (asc_type === "corp") {
            $("#sec_article_of_incorporation").show();
        }else{
            $("#sec_article_of_incorporation").hide();
        }
    });

	$(document).on('change', '#region', function(event){
        var region  = $('#region').val();
        $.ajax({
              url : "/get_city_asc",
              data: {
                  'region': region
              },
              beforeSend: function(){
                 $("#city").prop( "disabled", true ).next().css('display', "block");
              },
              success: function (data, textStatus, jqXHR) {
                 $("#city").prop( "disabled", false ).next().css('display', "none");;
              },
          })
          .then(function(result){
              if (result) {
                  $('#city').html(result);
              }
          });
    });

});

$("#company_name_check").hide();
$("#mob_no_code_check").hide();
$("#mob_no_check").hide();
$("#email_check").hide()

function validatefirstpage() {

        let validations = [];
        $("form#registration-form span.val-msg").remove();


        // company name
        if ( $('#lname').val() == '') {
            $('#lname').after("<span class='val-msg'>* Company name is required</span>");
            validations.push('lname');
        }

        if ( $('#region').val() == '' ) {
            $('#region').after("<span class='val-msg'>* Region/Province is required</span>");
            validations.push('region');
        }

        // mobile number
        let mob_no_code = $("#mob_no_code").val();
        let mob_no = $('#mob_no').val();
        let isValidEntry = !(mob_no_code === '' || mob_no_code.length !== 3 || mob_no === '' || mob_no.length !== 10);
	    if (!isValidEntry) {
          $('#mob_no').after("<span class='val-msg'>* Mobile number is invalid</span>");
          validations.push('mob_no');
	    } else  {
            var isValid_mob_code = /^\+[0-9]{2}$/.test(mob_no_code);
			var isValid_mob_no = /^[0-9]*$/.test(mob_no);
            let is_valid = isValid_mob_code && isValid_mob_no;
			if (!is_valid) {
                $('#mob_no').after("<span class='val-msg'>* Mobile number is invalid</span>");
                validations.push('mob_no');
            }
	    }

        // email
        if ( $('#email').val() == '') {
            $('#email').after("<span class='val-msg'>* E-mail is Required</span>");
            validations.push('email');
        } else {
            var regex = /^([a-zA-Z0-9_\.\-\+])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
            var email = $('#email').val();
            if(!regex.test(email)) {
                $('#email').after("<span class='val-msg'>* Please enter a valid email address</span>");
                validations.push('email-invalid');
            }
        }

        if (validations.length > 0) {
            return false;
        } else {
            return true;
        }
  }

function validatesecondpage() {
    let result = "true"
    var asc_type = $("input[type='radio'][name='asc_type']:checked").val();
    const attachment = document.querySelectorAll('.attachment_input')
    if (asc_type === "corp") {
        attachment.forEach(attachment => {
        const attachment_name = attachment.name
        if (attachment.value===""){
            $("."+attachment_name).show();
            result = "false"
            return false;
            }else{
            $("."+attachment_name).hide();
            }
            })
        }
        else{
        attachment.forEach(attachment => {
        const attachment_name = attachment.name
        if (attachment.value==="" && attachment.name != "sec_article_of_incorporation"){
            $("."+attachment_name).show();
            result = "false"
            return false;
            }else{
            $("."+attachment_name).hide();
            }
            })
        }
	    return result;
  }

$(document).on('change', '.attachment_input', function(event){
    const attachment = document.querySelectorAll('.attachment_input')
    attachment.forEach(attachment => {
    const attachment_name = attachment.name
    if (attachment.value) {
	            var filename = attachment.value;
	            var extension = filename.substr(filename.lastIndexOf("."));
                var allowedExtensionsRegx = /(\.pdf)$/i;
	            var isAllowed = allowedExtensionsRegx.test(extension);

            	if (!isAllowed) {
            		$("."+attachment_name).text('Invalid format. Please upload a .pdf file.');
	            	$("."+attachment_name).show();
	            	$("#join_now").attr('disabled', true);
	                return false;
	            } else if(attachment.files[0].size > 1000000) {
	            	$("."+attachment_name).text('The maximum size should be 1 MB!');
	            	$("."+attachment_name).show();
	            	$("#join_now").attr('disabled', true);
	                return false;
	            }
	            else{
	            	$("."+attachment_name).hide();
	            	$("#join_now").attr('disabled', false);
	            }

            }
    	})
        });
	
});



