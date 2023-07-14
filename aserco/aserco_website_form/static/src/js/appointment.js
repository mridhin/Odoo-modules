odoo.define('aserco_website_form.appointment', require => {
    'use strict';

    /*
      Added Method to Get value of Service type
  */
$(document).on('change', '#ooatg10rhyw', function(event){
   var service_type  = $('#ooatg10rhyw').val();

      $.ajax({
          url : "/get_area",
          data: {
              'service_type': service_type
          },
      })
      .then(function(result){
          console.log(result)
          if (result) {
              $('#okg1p4jr9pzo').html(result);

          }
      });

});

    /*
      Added Method to Get value of Service type, Area, Time slot
  */
$(document).on('change', '#okg1p4jr9pzo, #ooatg10rhyw, #onfx304tmmt0, #onfx304tmmt1', function(event){
   var service_type  = $('#ooatg10rhyw').val();
   var area  = $('#okg1p4jr9pzo').val();
   var timeslot = $("input[type='radio'][name='x_studio_preferred_time_slot']:checked").val();

      $.ajax({
          url : "/get_available_dates",
          data: {
              'service_type': service_type,
              'area': area,
              'timeslot': timeslot
          },
      })
      .then(function(result){
          console.log(result)
          if (result) {
              $('#x_studio_preferred_service_schedule').html(result);
          }
      });

});

});
