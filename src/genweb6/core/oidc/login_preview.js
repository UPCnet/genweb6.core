function updatePreview() {
  $("#headingCAS").html($("#login_preview_text").text() + " " + $("#form-widgets-login_text_btn").val());
}

$(document).ready(function(){
  updatePreview();

  $("#form-widgets-login_text_btn").on('keyup', function(){
    updatePreview();
  });
})
