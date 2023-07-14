odoo.define('awb_website.website_nav_js',function(require){
$(document).ready(function () {
    var url = window.location.pathname
	$('.nav-link').each(function () {
	url1 =  $(this).attr('href')
	if(url === url1){
	   $(this).addClass('active');
	   }
	})
	$('.nav-link').on('click', function (e) {
	    $(this).addClass('active')
	});


	$("#show-more").click(function() {
        $(".grid-container > div:hidden").show();
        $(this).hide();
        $("#show-less").show();
     });

     $("#show-less").click(function() {
        $(".grid-container > div:not(:nth-child(-n+4))").hide();
        $(this).hide();
        $("#show-more").show();
      });
	});
	jQuery(document).ready(function($) {
    var silder = $("#home-testimonials");
    silder.owlCarousel({
        autoplay: true,
        autoplayTimeout: 3000,
        autoplayHoverPause: false,
        items: 1,
        center: true,
        nav: false,
        margin: 50,
        dots: true,
        loop: true,
        itemsMobile: true,
        responsive : {
      768 : {
        items: 2,
        center: true,
      },
      0:{
        items:1,
      }
    }
    });
});
});
