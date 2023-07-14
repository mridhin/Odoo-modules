var faq = document.getElementsByClassName("faq-page");
var i;
for (i = 0; i < faq.length; i++) {
    faq[i].addEventListener("click", function () {
        this.classList.toggle("active_faq");
        var body = this.nextElementSibling;
        if (body.style.display === "block") {
            body.style.display = "none";
        } else {
            body.style.display = "block";
        }
    });
}
jQuery(document).ready(function($) {
    var silder = $("#store-testimonials");
    silder.owlCarousel({
        autoplay: false,
        autoplayTimeout: 3000,
        autoplayHoverPause: false,
        items: 1,
        nav: true,
        margin: 50,
        dots: false,
        loop: false,
        itemsMobile: true,
        navText : ['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>'],
        responsive : {
      1200 : {
        items: 3,
      },
      768 : {
        items: 2,
      },
      518 : {
        items: 2,
      },
      0:{
        items:1,
      }
    }
    });
});
$(document).on('click', '.read_more', function(event){
var dots = event.target.previousElementSibling.querySelector(".dots");
  var moreText = event.target.previousElementSibling.querySelector(".more");
  var btnText = event.target;

  if (dots.style.display === "none") {
    dots.style.display = "inline";
    btnText.innerHTML = "Read more";
    moreText.style.display = "none";
    event.target.style.height = "auto";
  } else {
    dots.style.display = "none";
    btnText.innerHTML = "Read less";
    moreText.style.display = "inline";
  }

});
if ($(window).width() < '1038'){
    var element = document.querySelectorAll("#item_row");
    for (i = 0; i < element.length; i++) {
         element[i].classList.remove("row");
    }
}

