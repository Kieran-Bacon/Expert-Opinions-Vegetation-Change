function uploadQuestion(){

    var text = $("#QuestionInput").val();
    console.log("Pressed the submit button");
    console.log(text);


	$.ajax({
		"url": "/createQuestion",
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"text":text},
		"success": function(data, status){
            $("#QuestionInput").val("");
            $("#questionTBody").append("<tr id='questionrow-"+data.qid+"'><td>"+data.qid+"</td><td>"+text+"</td><td><button type='button' class='btn btn-danger btn-circle' onclick='deleteQuestion("+data.qid+");'><i class='fa fa-trash-o'></i></button></td></tr>");
        },
        "failure": function(data, status){
            console.log("failed");
        }
	});
}

function deleteQuestion(qid){
	$.ajax({
		"url": "/deleteQuestion",
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"qid":qid},
		"success": function(data, status){
            $("#questionrow-" + qid).remove();
        },
        "failure": function(data, status){
            console.log("failed");
        }
	});
}