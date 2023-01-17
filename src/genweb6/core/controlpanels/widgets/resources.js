function showOptions() {
    var value = $("#form-widgets-upload_files-0")[0].checked;

    if (value) {
      $('#formfield-form-widgets-text_css').hide();
      $('#formfield-form-widgets-text_js').hide();
      $('#formfield-form-widgets-file_css').show();
      $('#formfield-form-widgets-file_js').show();
    } else {
      $('#formfield-form-widgets-text_css').show();
      $('#formfield-form-widgets-text_js').show();
      $('#formfield-form-widgets-file_css').hide();
      $('#formfield-form-widgets-file_js').hide();
    }
}

$(document).ready(function(){

  showOptions();

  $("#form-widgets-upload_files-0").on("change", function(){
    showOptions();
  });

});
