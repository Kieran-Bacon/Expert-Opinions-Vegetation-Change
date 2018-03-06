function resetPassword(){

    var username = $("#usernameInput").val();

    console.log(username);

	$.ajax({
		"url": "/password_reset",
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"username": username},
		"success": function(data, status){

            console.log(data);
            console.log(status);
            new PNotify({
                title: data.title,
                text: data.text,
                type: data.type,
                styling: 'fontawesome'
            });
			
		},
		"error": function(data, status){
            // TODO Not doing anything
			new PNotify({
                title: 'Error when connecting to server',
                text: data.responseText,
                type: 'error',
                styling: 'fontawesome'
            });
		}
	});
}