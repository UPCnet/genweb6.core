$(document).ready(function() {

  // Use bootstrap classes for add portlet dropdown
  $('select.add-portlet').change(function(event) {
    event.preventDefault();
    event.stopPropagation();
    $(this).parent().submit();
  });

  // Call the ws that stores the span value given a portletManager
  $('.editable').bind('change', function(event) {
    // event.preventDefault()
    // event.stopPropagation()
    data = {'manager': $(this).data()['manager'],
            'contextId': $(this).data()['contextId'],
            'span': $(this).val()};
    $.ajax({
      url: data.contextId + "/@@set-portlethomemanager-span",
      data: data,
      type: 'POST',
      success: function(data){
          alertify.success("Configuració guardada.");
      },
      error: function(){
          alertify.error("Error al guardar la configuració.");
      }
    });
  });
});
