function completeAccount(){
    // Collect the e-mail address, will be validating server side so no need to validate.
    username = $("#username").val();
    pwd =  $("#pwd").val();
    cpwd = $("#cpwd").val();
    title = $("#title").val();
    firstname = $("#firstname").val();
    lastname = $("#lastname").val();
    organisation = $("#organisation").val();
    email = $("#email").val();

    if(email == ""){
        // Inform the user they have not entered the e-mail address yet
        new PNotify({
            title: 'Need an e-mail address first!',
            text: 'Please write in the e-mail address of the user you would like to invite, before submitting the invitation.',
            type: 'info',
            styling: 'fontawesome'
        });
        return
    }

    // Send address to the server
	$.ajax({
		"url": window.location.pathname,
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"username":username,"title":title,"firstname":firstname,"lastname":lastname,"organisation":organisation,"email":email,"password":pwd},
		"success": function(data, status){
            window.location.pathname = "/login.html";
        },
        "error": function(data, status){
            new PNotify({
                title: 'Failed to confirm account',
                text: 'Ow no! The server was unable to fulfil this request because: ' + data.responseText,
                type: 'error',
                styling: 'fontawesome'
            });
        }
	});

};