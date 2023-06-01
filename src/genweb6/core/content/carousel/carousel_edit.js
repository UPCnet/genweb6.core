function showCollectionSelector() {
    var value = $('select#form-widgets-content').val();

    switch(value) {
      case 'inside':
        if ($('body.template-edit').length > 0) {
            $('#formfield-form-widgets-content .form-text').show();
        } else {
            $('#formfield-form-widgets-content .form-text').hide();
        }
        $('#formfield-form-widgets-collection').hide();
        break;

      default:
        $('#formfield-form-widgets-content .form-text').hide();
        $('#formfield-form-widgets-collection').show();
        break;
    }
}

$(document).ready(function(){

    showCollectionSelector();

    $('select#form-widgets-content').on('change', function(){
        showCollectionSelector();
    });
});
