$(document).ready(function() {

  $('.carousel-control-pause').click(function() {

    var carousel = $(this).closest('.carousel');

    if (carousel.hasClass('paused')) {
      carousel.carousel('cycle');
      carousel.removeClass('paused');
    } else {
      carousel.carousel('pause');
      carousel.addClass('paused');
    }

    var icon = $(this).find('.bi-pause-fill');

    if (icon.length) {
      icon.removeClass('bi-pause-fill').addClass('bi-play-fill');
    } else {
      icon = $(this).find('.bi-play-fill');
      icon.removeClass('bi-play-fill').addClass('bi-pause-fill');
    }

  });

});