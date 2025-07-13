$(document).ready(function () {
   

    // 👇 Animate product detail container on page load
    $(".product-detail-container").css({
        opacity: 0,
        position: "relative",
        top: "20px"
    }).animate({
        opacity: 1,
        top: "0px"
    }, 600);
});
