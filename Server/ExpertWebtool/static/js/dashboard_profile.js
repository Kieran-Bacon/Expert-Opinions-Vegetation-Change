$(document).ready(function(){

})

function submitBatch(qid){
    $.ajax({
		"url": "/training/submitBatch",
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"qid": qid},
		"success": function(data, status){

            // Notify the user on the success
            new PNotify({
                title: "Batch has begun training!",
                text: "The models you have annotated have are now being used in our training process. Your representation will now include this information",
                type: 'success',
                styling: 'fontawesome'
            });

            // Remove the batch row from the screen
            $("#batchRow" + qid).remove();
		},
		"error": function(data, status){
            // report error to the user
			new PNotify({
                title: 'Error when connecting to server',
                text: data.responseText,
                type: 'error',
                styling: 'fontawesome'
            });
		}
	});
};

function removeBatch(qid){

    if(confirm("Are you sure you want to remove this batch?")){
        $.ajax({
            "url": "/training/removeBatch",
            "type": "POST",
            "contentType": "application/x-www-form-urlencoded",
            "data": {"qid": qid},
            "success": function(data, status){
                new PNotify({
                    title: 'Batch information removed',
                    text: "Your feature information has been removed, you will now be able to annotate those particular models again from the training page.",
                    type: 'success',
                    styling: 'fontawesome'
                });

                // Remove the batch row from the screen
                $("#batchRow" + qid).remove();
            },
            "error": function(data, status){
                new PNotify({
                    title: 'Error when connecting to server',
                    text: data.responseText,
                    type: 'error',
                    styling: 'fontawesome'
                });
            }
        });
    } else {
        new PNotify({
            title: 'Whew!',
            text: "Your information has not been removed.",
            type: 'info',
            styling: 'fontawesome'
        });
    }
};