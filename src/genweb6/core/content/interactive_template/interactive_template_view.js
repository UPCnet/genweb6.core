function copyToClipboard(element) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val("<iframe class='w-100 resizeIframe' src='" + $('body').attr('data-view-url') + "/simple'></iframe>").select();
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
