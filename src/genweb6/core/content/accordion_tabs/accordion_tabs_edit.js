function showElementsType() {
    var value = $('select#form-widgets-type_template').val();

    switch(value) {
      case '--NOVALUE--':
        $('#formfield-form-widgets-accordion_open_multiple').hide();
        $('#formfield-form-widgets-accordion_open_first').hide();
        break;
      case 'accordion':
        $('#formfield-form-widgets-accordion_open_multiple').show();
        $('#formfield-form-widgets-accordion_open_first').show();
        break;
      case 'nav':
        $('#formfield-form-widgets-accordion_open_multiple').hide();
        $('#formfield-form-widgets-accordion_open_first').hide();
        break;
    }
}

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

    showElementsType();
    showCollectionSelector();

    $('select#form-widgets-type_template').on('change', function(){
        showElementsType();
    });

    $('select#form-widgets-content').on('change', function(){
        showCollectionSelector();
    });
});
