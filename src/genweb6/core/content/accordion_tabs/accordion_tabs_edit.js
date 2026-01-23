function showElementsType() {
  var value = $('select#form-widgets-type_template').val();

  switch(value) {
    case '--NOVALUE--':
      $('#formfield-form-widgets-accordion_open_multiple').hide();
      $('#formfield-form-widgets-accordion_open_first').hide();
      $('#formfield-form-widgets-accordion_items_expanded').hide();
      break;
    case 'accordion':
      $('#formfield-form-widgets-accordion_open_multiple').show();
      $('#formfield-form-widgets-accordion_open_first').show();
      $('#formfield-form-widgets-accordion_items_expanded').show();
      break;
    case 'nav':
      $('#formfield-form-widgets-accordion_open_multiple').hide();
      $('#formfield-form-widgets-accordion_open_first').hide();
      $('#formfield-form-widgets-accordion_items_expanded').hide();
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

function disableSecondaryCheckboxIfPrincipalIsChecked(principal_checkbox, secondary_checkbox, enable_secondary_checkbox = false) {
  if (principal_checkbox.length === 0 || secondary_checkbox.length === 0) {
    return;
  }
  
  var isOpenFirstChecked = principal_checkbox.is(':checked');
  if (isOpenFirstChecked) {
    secondary_checkbox.prop('disabled', true);
    if (enable_secondary_checkbox) {
      secondary_checkbox.prop('checked', true);
    } else {
      secondary_checkbox.prop('checked', false);
    }
  } else {
    secondary_checkbox.prop('disabled', false);
  }
}

$(document).ready(function(){

  showElementsType();
  showCollectionSelector();
  disableSecondaryCheckboxIfPrincipalIsChecked($('#form-widgets-accordion_open_first input[type="checkbox"]'), $('#form-widgets-accordion_items_expanded input[type="checkbox"]'));
  disableSecondaryCheckboxIfPrincipalIsChecked($('#form-widgets-accordion_items_expanded input[type="checkbox"]'), $('#form-widgets-accordion_open_first input[type="checkbox"]'));
  disableSecondaryCheckboxIfPrincipalIsChecked($('#form-widgets-accordion_items_expanded input[type="checkbox"]'), $('#form-widgets-accordion_open_multiple input[type="checkbox"]'), true);

  $('select#form-widgets-type_template').on('change', function(){
    showElementsType();
  });

  $('select#form-widgets-content').on('change', function(){
    showCollectionSelector();
  });

  $('#form-widgets-accordion_open_first input[type="checkbox"]').on('change', function(){
    disableSecondaryCheckboxIfPrincipalIsChecked($('#form-widgets-accordion_open_first input[type="checkbox"]'), $('#form-widgets-accordion_items_expanded input[type="checkbox"]'));
  });

  $('#form-widgets-accordion_items_expanded input[type="checkbox"]').on('change', function(){
    disableSecondaryCheckboxIfPrincipalIsChecked($('#form-widgets-accordion_items_expanded input[type="checkbox"]'), $('#form-widgets-accordion_open_first input[type="checkbox"]'));
    disableSecondaryCheckboxIfPrincipalIsChecked($('#form-widgets-accordion_items_expanded input[type="checkbox"]'), $('#form-widgets-accordion_open_multiple input[type="checkbox"]'), true);
  });
  
});
