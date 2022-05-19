function reloadResultsFilter() {
  var query = $('#searchinputcontent .searchInputPretty').val();
  var path = $('#librarysearchpretty #searchinputcontent .searchInputPretty').data().name;
  var tags = [];
  $('.searchbytagcontainer input[name="tag"]:checked').each(function(){
    tags.push($(this).val());
  });

  $.get(path, { q: query, t: tags.join(',') }, function(data) {
    $('#tagslist').html(data);
  });
}

$(document).ready(function(){

  setTimeout(function(){
    reloadResultsFilter();
  }, 500);

  $('.searchbytagcontainer input[name="tag"]').on("change", function(e) {
    reloadResultsFilter();
  });

  $('#librarysearchpretty #searchinputcontent .searchInputPretty').on('keyup', function(event) {
    reloadResultsFilter();
  });

  /*if($('body.template-filtered_contents_search_pretty_view.userrole-anonymous').length || $('body.template-filtered_contents_search_complete_pretty_view.userrole-anonymous').length){
    $('#edit-bar').remove();
  }*/

});
