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


function showAutoStart() {
    var value = $('select#form-widgets-carousel_type').val();

    switch(value) {
      case 'simple':
        $('#formfield-form-widgets-carousel_enable_auto_start').show();
        break;

      default:
        $('#formfield-form-widgets-carousel_enable_auto_start').hide();
        break;
    }
}

function showInterval() {
    var value = $('select#form-widgets-carousel_type').val();

    switch(value) {
      case 'simple':
        if ($('#form-widgets-carousel_enable_auto_start input').is(':checked')) {
            $('#formfield-form-widgets-carousel_interval').show();
        } else {
            $('#formfield-form-widgets-carousel_interval').hide();
        }
        break;

      default:
        $('#formfield-form-widgets-carousel_interval').hide();
        break;
    }
}


$(document).ready(function(){

    showCollectionSelector();
    showAutoStart();
    showInterval();

    $('select#form-widgets-content').on('change', function(){
        showCollectionSelector();
    });

    $('select#form-widgets-carousel_type').on('change', function(){
        showAutoStart();
    });

    $('#form-widgets-carousel_enable_auto_start').on('change', function(){
        showInterval();
    });
});
