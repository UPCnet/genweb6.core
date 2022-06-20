function updatePreview(lang) {
  var text = "";

  if ($("#form-widgets-enable_alternative_text-0").is(':checked')){
    switch(lang){
      case 'ca':
        text = $("#form-widgets-alternative_text_ca").val();
        break;
      case 'es':
        text = $("#form-widgets-alternative_text_es").val();
        break;
      case 'en':
        text = $("#form-widgets-alternative_text_en").val();
        break;
    }
  }else{
    text = $("#cookies_preview_text").html();
  }

  $("#cookies-gw-preview #cookies-bodyText").html(text);
}

$(document).ready(function(){
  updatePreview();

  $("#form-widgets-enable_alternative_text-0").on('change', function(){
    updatePreview('ca');
  });

  $("#form-widgets-alternative_text_ca").on('keyup', function(){
    updatePreview('ca');
  });

  $("#form-widgets-alternative_text_ca").on('click', function(){
    updatePreview('ca');
  });

  $("#form-widgets-alternative_text_es").on('keyup', function(){
    updatePreview('es');
  });

  $("#form-widgets-alternative_text_es").on('click', function(){
    updatePreview('es');
  });

  $("#form-widgets-alternative_text_en").on('keyup', function(){
    updatePreview('en');
  });

  $("#form-widgets-alternative_text_en").on('click', function(){
    updatePreview('en');
  });
})
