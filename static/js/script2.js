$(document).ready(function () {
    // Slide-up animation for register form
    $(".form-wrapper").css({
        opacity: 0,
        position: "relative",
        top: "40px"
    }).animate({
        opacity: 1,
        top: "0"
    }, 700);
});
