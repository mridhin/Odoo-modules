$(document).ready(function(){

    $(document).on('click', '.rating_icon', function(event){
        $(".rating_icon").removeClass('checked');
        rating_value = $(this).data('rating');
        $(".rating_val").val(rating_value);
        for(var i = 1; i <= rating_value; i++) {
            $(".rating_icon_"+i).addClass('checked');
        }
    });


  
});