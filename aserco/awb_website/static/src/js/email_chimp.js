odoo.define('awb_website.email_chimp',function(require){

    var EMAIL_CHIMP = {};
    $(document).ready(function(){
        // Disable the Subscribe button
        $('#mc-embedded-subscribe').prop('disabled', true);


        $('#mc-embedded-subscribe').on('click', function (e) {
            $('#mce-error-response').css('display', 'none');
            $('#mce-success-response').css('display', 'none');
            console.log('### CLICKED SUBSCRIBED');
            var regex = /^([a-zA-Z0-9_\.\-\+])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
            var email = $('#mce-EMAIL').val();

            var xxxx = $('#mail-checkbox').prop('checked');
            console.log('IS CHECKED?? >>>>>>>>>> ' + xxxx)


            if (!$('#mail-checkbox').prop('checked')) {
              // Disable the button
              $('#mc-embedded-subscribe').prop('disabled', true);
              return false;
            }

            if(!regex.test(email)) {
                console.log('WRONG EMAIL');
                $('#mce-error-response').css('display', 'block').text('Please enter a valid email address.');
                $('#mce-success-response').css('display', 'none');
            } else {
                $('#mce-error-response').css('display', 'none');
                $('#mce-success-response').css('display', 'none');

            }
        });

        $('#mail-checkbox').on('change', function() {
             $('#mce-error-response').css('display', 'none');
             $('#mce-success-response').css('display', 'none');

            // Check if the checkbox is checked
            if ($(this).prop('checked')) {
              // Disable the button
              $('#mc-embedded-subscribe').prop('disabled', false);

            } else {
              // Enable the button
              $('#mc-embedded-subscribe').prop('disabled', true);
            }
        });
    });
});
