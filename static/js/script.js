$(document).ready(function () {
    // Hover animation
    $(".nav-links li a").hover(
        function () {
            $(this).animate({ fontSize: "18px" }, 200);
        },
        function () {
            $(this).animate({ fontSize: "16px" }, 200);
        }
    );

    // Mobile menu toggle
    $("#mobile-menu").click(function () {
        $(".nav-links").toggleClass("active");
    });
});

$(document).ready(function () {
        const $searchInput = $('.search-input');

        $searchInput.on('focus', function () {
            $(this).stop().animate({
                width: '260px'
            }, 300);
        });

        $searchInput.on('blur', function () {
            // Only shrink if input is empty
            if (!$(this).val()) {
                $(this).stop().animate({
                    width: '160px'
                }, 300);
            }
        });
    });
