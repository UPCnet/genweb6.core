function update_new_existing_content_type(selected_option) {
  switch(selected_option) {
    case 'EXTERN':
      $('#formfield-form-widgets-own_content').hide();
      $('#formfield-form-widgets-external_url').show();
      break;
    case 'INTERN':
      $('#formfield-form-widgets-own_content').show();
      $('#formfield-form-widgets-external_url').hide();
      break;
    default:
      $('#formfield-form-widgets-own_content').hide();
      $('#formfield-form-widgets-external_url').hide();
  }
}

update_new_existing_content_type($("select[id='form-widgets-content_or_url']").val());
$("select[id='form-widgets-content_or_url']").change(function(){
    update_new_existing_content_type($(this).val());
});
