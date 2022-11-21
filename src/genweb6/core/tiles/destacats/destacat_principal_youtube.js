$('.video-youtube').click(function(){
  var target = $(this).attr('data-bs-target');
  var myModal = target;
  var videoSrc = $(myModal + " iframe").attr("src");

  $(myModal).on('hidden.bs.modal', function (e) {
    $(myModal + " iframe").attr("src", videoSrc);
  });
});
