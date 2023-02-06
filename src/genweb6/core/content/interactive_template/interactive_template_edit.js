function showHideAccordion(show) {
    if (show) {
        $('#formfield-form-widgets-accordion_open_multiple').show();
        $('#formfield-form-widgets-accordion_open_first').show();
    } else {
        $('#formfield-form-widgets-accordion_open_multiple').hide();
        $('#formfield-form-widgets-accordion_open_first').hide();
    }
}

function showHideCarousel(show) {
    if (show) {
        $('#formfield-form-widgets-carousel_type').show();
        $('#formfield-form-widgets-carousel_show_title').show();
        $('#formfield-form-widgets-carousel_show_description').show();
        $('#formfield-form-widgets-carousel_auto').show();
        $('#formfield-form-widgets-carousel_time').show();
    } else {
        $('#formfield-form-widgets-carousel_type').hide();
        $('#formfield-form-widgets-carousel_show_title').hide();
        $('#formfield-form-widgets-carousel_show_description').hide();
        $('#formfield-form-widgets-carousel_auto').hide();
        $('#formfield-form-widgets-carousel_time').hide();
    }
}

function showHideSlide(show) {
    if (show) {
        $('#formfield-form-widgets-slide_size').show();
        $('#formfield-form-widgets-slide_time').show();
    } else {
        $('#formfield-form-widgets-slide_time').hide();
        $('#formfield-form-widgets-slide_size').hide();
    }
}

function showHideModal(show) {
    if (show) {
        $('#formfield-form-widgets-modal_type_btn').show();
    } else {
        $('#formfield-form-widgets-modal_type_btn').hide();
    }
}

function showElementsType() {
    var value = $('select#form-widgets-type_template').val();

    switch(value) {
      case '--NOVALUE--':
        showHideAccordion(false);
        showHideCarousel(false);
        showHideSlide(false);
        showHideModal(false);
      case 'accordion':
        showHideAccordion(true);
        showHideCarousel(false);
        showHideSlide(false);
        showHideModal(false);
        break;
      case 'nav':
        showHideAccordion(false);
        showHideCarousel(false);
        showHideSlide(false);
        showHideModal(false);
        break;
      case 'carousel':
        showHideAccordion(false);
        showHideCarousel(true);
        showHideSlide(false);
        showHideModal(false);
        break;
      case 'imatge-slide':
        showHideAccordion(false);
        showHideCarousel(false);
        showHideSlide(true);
        showHideModal(false);
        break;
      case 'modal':
        showHideAccordion(false);
        showHideCarousel(false);
        showHideSlide(false);
        showHideModal(true);
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
      case 'collection':
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
