$('#loginBtn').on('click', function(){

    $('#loginModal .modal-body').load($('#loginBtn').data('url'), function(){

        $('#loginModal').modal( { show:true } );

    });

});
