Dropzone.autoDiscover = false;

var hasEvaluated = false;

var switches = [];
var modelsUploaded = false;

var expertList = [];
var questionList = [];



$(document).ready(function() {

	// 
    var elems = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));
	elems.forEach(function(html) {
		var switchery = new Switchery(html);
		switches.push(switchery);
	});

	

	// Create the dropzone - set up function on successful upload
	var myDropzone = new Dropzone("#modelDropzone");
	myDropzone.on("success", function(file, resp) {modelsUploaded = true;});

	$(".setup_tabs").on("click", function(e){
		if(hasEvaluated){
			hasEvaluated = false;
			modelsUploaded = false;
			$("#EvaluationTables").empty();

			for(var i = 0; i<switches.length;i++){
				if(switches[i].element.checked){
					$("#" + switches[i].element.id).trigger("click");
				}
			}

			expertList = [];
			questionList = [];

			myDropzone.removeAllFiles();
		}
	});

	// 
	$("#evalTab").on("click", function(e){

		var reasons = validation();
		if(!reasons.length){
			hasEvaluated = true;
			evaluateModels();
		}
		else {
			$.each(reasons, function(index, value){
				value["type"] = "error";
				value["styling"] = "fontawesome";
				new PNotify(value);
			})
			e.preventDefault();
    		return false;
		}
	})
});

function evaluateModels(){
	// Send information to the server and process it
	console.log(expertList);
	console.log(questionList);

	$.ajax({
		"url": "/evaluation",
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"experts": expertList, "questions": questionList},
		"success": function(data, status){

			console.log(data);

			$.each(data.questions, function(i, quest){

				// Assign the name of the table of results
				var tableTitle = document.createElement("h4");
				tableTitle.innerHTML = quest.text;

				// Create the table object
				var table = document.createElement("table");
				table.setAttribute("class","table");

				// Generate the header information for the table
				var header = document.createElement("thead");
				var tr = document.createElement("tr");
				var th = document.createElement("th");
				var rowHeader = document.createTextNode("Models");

				th.appendChild(rowHeader);
				tr.appendChild(th);

				$.each(data.experts, function(index, name){
					var th = document.createElement("th");
					var expertTextNode = document.createTextNode(name);
					th.appendChild(expertTextNode);
					tr.appendChild(th);
				});

				header.appendChild(tr);
				table.appendChild(header);

				// Generate the body of the table
				var body = document.createElement("tbody");
				$.each(quest.models, function(j, model){

					var bodyRow = document.createElement("tr");
					var modelName = document.createElement("td");
					var nameNode = document.createTextNode(model.name)
					modelName.appendChild(nameNode);
					bodyRow.appendChild(modelName);

					$.each(model.values, function(k, prediction){
						var td = document.createElement("td");
						var tdContent = document.createTextNode(prediction);
						td.appendChild(tdContent);
						bodyRow.appendChild(td);
					});

					body.appendChild(bodyRow);
				});

				// Add the body to the table
				table.appendChild(body);

				// Add the new table to the page
				$("#EvaluationTables").append(tableTitle);
				$("#EvaluationTables").append(table);
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

function validation(){

	var experts = 0;
	var questions = 0;
	expertList = [];
	questionList = [];

	$.each(switches, function(i,v){
		if(v.element.id.split("-")[0] == "user" && v.element.checked){
			expertList.push(v.element.id.split("-")[1]);
			experts++;
		}
		if(v.element.id.split("-")[0] == "question" && v.element.checked){
			questionList.push(v.element.id.split("-")[1]);
			questions++;
		}
	});

	var reasons = [];
	// Check that at least an expert has been selected
	if(!experts){
		reasons.push({"title": "Please select some experts", "text": "You need to select at least one expert to do the evaluation."})
	}

	if(!questions){
		reasons.push({"title":"Please select some questions", "text": "You need to select questions that we'll ask to those experts."})
	}

	if(!modelsUploaded){
		reasons.push({"title": "Please provide some climate model ouputs", "text": "You need to upload some valid climate model outputs for evaluation"})
	}

	return reasons
};
