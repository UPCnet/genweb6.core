$(document).ready(function() {

  $(".portlet.portlet-rss .description").each(function(){
    $(this).html($(this).text());
  });

  $(".portlet.portlet-rss  a[rel='external']").attr("target", "_blank");

});
