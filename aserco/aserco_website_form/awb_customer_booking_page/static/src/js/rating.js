var BOOKING = {};
$(document).ready(function(){
    $('.readonly').keydown(function(e) {
        if (e.keyCode === 8 || e.keyCode === 46)  // Backspace & del
            e.preventDefault();
        }).on('keypress paste cut', function(e) {
            e.preventDefault();
        });

    BOOKING.binding = function() {
        $(document).on('change', '#service-needed', function(event){
            var service_type  = $('#service-needed').val();
            var region  = $('#region_booking').val();
            var timeslot = $("input[type='radio'][name='options']:checked").val();
            $("#date_start").val("");
            $("#date_start").datepicker('destroy');
            BOOKING.bindDatePicker(region, service_type, timeslot);
        });
        $(document).on('change', '#region_booking', function(event){
            let service_type  = $('#service-needed');
            let region  = $('#region_booking');
            let timeslot = $("input[type='radio'][name='options']:checked").val();
            let city = $('#city');
            let barangay = $('#barangay');

            $("#date_start").val("");
            $("#date_start").datepicker('destroy');

            city.html("");
            barangay.html("");

            city.prop('disabled', true ).next().css('display', "none");
            barangay.prop('disabled', true ).next().css('display', "none");

            if( region.val() != "-select-" ) {
                $.ajax({
                    url : "/get_city",
                    data: {
                        'region': region.val()
                    },
                    beforeSend: function(){
                        city.prop( "disabled", true ).next().css('display', "block");
                        barangay.prop( "disabled", true ).next().css('display', "none");
                    },
                    success: function (data, textStatus, jqXHR) {
                        city.prop( "disabled", false ).next().css('display', "none");
                    },
                }).then(function(result){
                    if (result) {
                        city.html(result);
                    }
                });

//                $.ajax({
//                      url : "/get_barangay",
//                      data: {
//                          'city': city.val()
//                      },
//                      success: function (data, textStatus, jqXHR) {
//                         barangay.prop( "disabled", false ).next().css('display', "none");
//                      },
//                  })
//                 .then(function(result){
//                      if (result) {
//                        barangay.html(result);
//                      }
//                 });
                 BOOKING.bindDatePicker(region.val(), service_type.val(), timeslot);
            }
        });
        $(document).on('change', '#city', function(event){

            let city = $('#city');
            let barangay = $('#barangay');
            barangay.html("");
            barangay.prop('disabled', true ).next().css('display', "none");

            if ( city.val() != "" ){
                $.ajax({
                      url : "/get_barangay",
                      data: {
                          'city': city.val()
                      },
                      beforeSend: function(){
                         barangay.prop( "disabled", true ).next().css('display', "block");
                      },
                      success: function (data, textStatus, jqXHR) {
                         barangay.prop( "disabled", false ).next().css('display', "none");
                      },
                      error: function (request, status, error) {
                        barangay.prop( "disabled", false ).next().css('display', "none");
                        console.log('ERROR2: ' + error)
                      }
                }).then(function(result){
                      if (result) {
                        barangay.html(result);
                      }
                });
            }

        });
        $('#booking_form').submit(function(e){

            var validations = [];
            $("form#booking_form span.val-msg").remove();

            let lname = $('#lname').val();
            let region = $('#region_booking').val();


            if ( $('#service-needed').val() == '-select-') {
                $('#service-needed').after("<span class='val-msg'>* Required</span>");
                validations.push('service-needed');
            }

             if ( $('#lname').val() == '') {
                $('#lname').after("<span class='val-msg'>* Required</span>");
                validations.push('lname');
            }

            if ( $('#fname').val() == '') {
                $('#fname').after("<span class='val-msg'>* Required</span>");
                validations.push('fname');
            }

             if ( $('#email').val() == '') {
                $('#email').after("<span class='val-msg'>* Required</span>");
                validations.push('email');
            } else {
                var regex = /^([a-zA-Z0-9_\.\-\+])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
                var email = $('#email').val();
                if(!regex.test(email)) {
                    $('#email').after("<span class='val-msg'>* Please enter a valid email address</span>");
                    validations.push('email-invalid');
                }
            }

            if ( $('#region_booking').val() == '-select-' ) {
                $('#region_booking').after("<span class='val-msg'>* Required</span>");
                validations.push('region-booking');
            }

            if ( $('#city').val() == '' ) {
                $('#city').after("<span class='val-msg'>* Required</span>");
                validations.push('city');
            }

            if ( $('#barangay').val() == '' ) {
                $('#barangay').after("<span class='val-msg'>* Required</span>");
                validations.push('barangay');
            }

            if ( $('#street').val() == '' ) {
                $('#street').after("<span class='val-msg'>* Required</span>");
                validations.push('street');
            }

            // if has available date. this validation is activated.
            if ( $('#booking-count').val() > 0 ) {
                if ( $('#date_start').val() == '' ) {
                    $('#date_start').after("<span class='val-msg val-msg-required'>* Required</span>");
                    validations.push('date_start');
                }
            }

             if ( $('#mobile').val() == '' ) {
                $('#mobile').after("<span class='val-msg'>* Required</span>");
                validations.push('mobile');
            }


            if (validations.length > 0) {
                return false;
            } else {
                return true;
            }

            e.preventDefault();
        });
    };
    BOOKING.triggerOnChange = function() {
        if ($('#service-needed').val() != '') {
            $("#service-needed").trigger("change");
        }
    };

    BOOKING.bindDatePicker = function(region, service_type, timeslot) {
         if(region != '-select-' && service_type != '-select-' && timeslot) {
                console.log('calling ajax - bindDatePicker...')
                $.ajax({
                  url : "/get_booking/available_dates",
                  data: {
                      'service_type': service_type,
                      'region': region,
                      'timeslot': timeslot
                  },
                  beforeSend: function(){
                    if( region != '-select-' && service_type != '-select-') {
                        $('span.val-msg-required, span.val-msg-booking').remove();
                        $('#date_start').after("<span class='val-msg-booking val-msg-loading'>Loading</span>");
                       $("#booking_button_submit").prop("disabled", true);
                       $("#region_booking").prop("disabled", true);
                       $("#service-needed").prop("disabled", true);
                    }
                     $("#date_start").prop( "disabled", true );
                  },
                  success: function (result) {
                    var myArray = result.split(",");
                    if (result != '' && myArray.length > 0) {
                      $('#booking-count').val(myArray.length);
                      var disableDates = function(date) {
                        var dmy = date.getDate() + "-" + (date.getMonth() + 1) + "-" + date.getFullYear();
                        return [
                          $.inArray(dmy, myArray) !== -1,
                          "my-class",
                          ($.inArray(dmy, myArray) !== -1 ? "Available" : "unAvailable")
                        ];
                      };
                      $("#date_start").datepicker({
                        beforeShowDay: disableDates,
                        changeMonth: true,
                        changeYear: true,
                        stepMonths: true,
                        minDate: new Date()
                      }).prop("disabled", false);
                      $('span.val-msg-loading, span.val-msg-booking').remove();
                      $("#booking_button_submit").prop("disabled", false);
                      $("#region_booking").prop("disabled", false);
                      $("#service-needed").prop("disabled", false);
                    } else {
                      $('#booking-count').val(0);
                      $('span.val-msg-loading, span.val-msg-required').remove();
                      $("#booking_button_submit").prop("disabled", false);
                      $("#region_booking").prop("disabled", false);
                      $("#service-needed").prop("disabled", false);
                      $('#date_start').after("<span class='val-msg-booking val-msg-no-result'>Your area is non serviceable at this time. If you wish to be contacted by our customer representative pls click submit.</span>");
                    }
                  },
                  error: function (request, status, error) {
//                       $('span.val-msg-loading').remove();
                         $('#date_start').after("<span class='val-msg-booking val-msg-no-result'>Something went wrong. Please try again later...</span>");
                        console.log('ERROR2: ' + error)
                      }
                });
         }
    }

    BOOKING.binding();
    BOOKING.triggerOnChange();
});