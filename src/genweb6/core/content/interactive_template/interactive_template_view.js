function copyToClipboard(element) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).html()).select();
    document.execCommand("copy");
    $temp.remove();
}

$(document).ready(function(){

    $('#copy-html').tooltip({
      animated: 'fade',
      placement: 'bottom',
      trigger: 'click',
    });

    $('#copy-html').on('click', function(){
        event.preventDefault();
        copyToClipboard('#interactive_template');
        return false;
    });

});
