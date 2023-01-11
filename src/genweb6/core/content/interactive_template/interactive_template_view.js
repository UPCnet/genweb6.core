function copyToClipboard(element) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).html()).select();
    document.execCommand("copy");
    $temp.remove();

    if($('#copy_html #remove_icon').length == 0){
        $('#copy_html').prepend('<i id="remove_icon" class="bi bi-check me-2"></i>');
        setTimeout(function(){
          $('#copy_html #remove_icon').remove();
        }, 5000);
    }
}

$(document).ready(function(){

    $('#copy_html').on('click', function(){
        event.preventDefault();
        copyToClipboard('#interactive_template');
        return false;
    });

});
