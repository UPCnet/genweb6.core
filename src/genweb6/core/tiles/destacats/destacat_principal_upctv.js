$('.video-upctv').click(function(){
  var myModal = $(this).attr('href');

  $(myModal).on('hidden.bs.modal', function (e) {
    $(myModal + " video").get(0).pause();
  });
});
