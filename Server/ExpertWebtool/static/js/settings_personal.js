$(document).ready(function() {

});

function saveChanges(){

    var model = $("#ModelSelect option:selected").val();
    
    // Send address to the server
	$.ajax({
		"url": "/settings/update_personal",
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"model_spec": model},
		"success": function(data, status){

            new PNotify({
                title: 'Personal settings changed',
                text: 'You changes to your personal settings has been saved and activated.',
                type: 'success',
                styling: 'fontawesome'
            });
        },
        "error": function(data, status){
            new PNotify({
                title: 'Failed to update!',
                text: 'Ow no! The server was unable to fulfil this request because: ' + data.responseText,
                type: 'error',
                styling: 'fontawesome'
            });
        }
	});
};