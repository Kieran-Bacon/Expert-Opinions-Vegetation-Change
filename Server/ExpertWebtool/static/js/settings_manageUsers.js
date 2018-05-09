$(document).ready(function() {
    $('#dataTables-example').DataTable({
        responsive: true
    });
});

function inviteUser(){
    // Collect the e-mail address, will be validating server side so no need to validate.
    title = $("#invite_title").val();
    firstname = $("#invite_firstname").val();
    lastname = $("#invite_lastname").val();
    organisation = $("#invite_organisation").val();
    email = $("#invite_email").val();
    permission = $("#invite_permission option:selected").val();

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
        "url": "/settings/invite_user",
        "type": "POST",
        "contentType": "application/x-www-form-urlencoded",
        "data": {"title":title,"firstname":firstname,"lastname":lastname,"organisation":organisation,"email":email, "permission":permission},
        "success": function(data, status){

            $("#invite_title").val("");
            $("#invite_firstname").val("");
            $("#invite_lastname").val("");
            $("#invite_organisation").val("");
            $("#invite_email").val("");

            new PNotify({
                title: 'User invite sent!',
                text: 'An invitation has been sent to the user, hope they join us soon!',
                type: 'success',
                styling: 'fontawesome'
            });
        },
        "error": function(data, status){
            new PNotify({
                title: 'Failed to invite user',
                text: 'Ow no! The server was unable to fulfil this request because: ' + data.responseText,
                type: 'error',
                styling: 'fontawesome'
            });
        }
    });

};