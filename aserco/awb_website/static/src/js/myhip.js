$(document).ready(function () {
   $("#html-item-pagination").hip({
   itemHeight:'200px',
   itemsPerPage:6,
   itemsPerRow:2,
   itemGaps:'20px',
   filter:true,
   filterPos:'center',
   paginationPos:'center'});
 });
 jQuery(document).ready(function($) {
    var silder = $("#footer-testimonials");
    silder.owlCarousel({
        autoplay: false,
        autoplayTimeout: 3000,
        autoplayHoverPause: false,
        items: 1,
        center: true,
        nav: false,
        margin: 50,
        dots: true,
        loop: true,
        itemsMobile: true,
    });
});