function showColoqiaOptions() {
    var enabled = $("#form-widgets-coloqia_enabled-0")[0].checked;
    var mode = $("#form-widgets-coloqia_mode").val();

    if (!enabled) {
      $('#formfield-form-widgets-coloqia_mode').hide();
      $('#formfield-form-widgets-coloqia_script').hide();
      $('#formfield-form-widgets-coloqia_url').hide();
      return;
    }

    $('#formfield-form-widgets-coloqia_mode').show();

    if (mode == 'url') {
      $('#formfield-form-widgets-coloqia_script').hide();
      $('#formfield-form-widgets-coloqia_url').show();
    } else {
      $('#formfield-form-widgets-coloqia_script').show();
      $('#formfield-form-widgets-coloqia_url').hide();
    }
}

$(document).ready(function(){

  showColoqiaOptions();

  $("#form-widgets-coloqia_enabled-0").on("change", function(){
    showColoqiaOptions();
  });

  $("#form-widgets-coloqia_mode").on("change", function(){
    showColoqiaOptions();
  });

});
