jQuery(function ($) {
  $('.newsImageContainer a').prepOverlay({subtype: 'image'});
  $('figcaption').css('max-width', $('.newsImageContainer img').width());
});
