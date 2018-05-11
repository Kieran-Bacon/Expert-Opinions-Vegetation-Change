Dropzone.autoDiscover = false;

var hasEvaluated = false;

var switches = [];
var modelsUploaded = false;

var expertList = [];
var questionList = [];

function ischecked(id){
    var check = false;
    $.each(switches, function(i,v){
        console.log(id, v.element.id);
        console.log(id == v.element.id);
        if(v.element.id == id){
            console.log(v.element.checked);
            console.log("Returning", v.element.checked);
            check = v.element.checked
        }
    });

    return check;
};

function displayExperts(qid){
// Collect the experts and display them to the page


    $.ajax({
        "url": "/evaluate_questionExperts",
        "type": "POST",
        "contentType": "application/x-www-form-urlencoded",
        "data": {"qid": qid},
        "success": function(data, status){
            console.log(data);

            var expert = document.createElement("div");
            expert.id = qid + "-container";

            cont = "";
            dataswitches = []
            $.each(data.experts, function(i,v){
                console.log("starting the loop",i,v);
                console.log(i);
                console.log(v);

                cont +='<div class="row" style="margin-bottom: 5px; background-color:cyan;">\
                            <div class="col-lg-1">\
                                <img style="width: 50px; height: auto;"src="'+v.avatar+'">\
                            </div>\
                            <div class="col-lg-9">\
                                <div class="col-lg-12"><p style="margin-bottom: 0px;">'+v.title+' '+v.firstname+' '+v.lastname+' , '+v.organisation+'</p></div>\
                                <div class="col-lg-12"><p style="margin-bottom: 0px;">\
                                    <i class="fa fa-expand" style="margin-right: 20px;"> '+v.precision+' </i>\
                                    <i class="fa fa-bullseye" style="margin-right: 20px;"> '+v.accuracy+' </i>\
                                    <i class="fa fa-tasks" style="margin-right: 20px;"> '+v.R2+' </i>\
                                    <i class="fa fa-bar-chart-o"> '+v.L1+' </i>\
                                </p></div>\
                            </div>\
                            <div class="col-lg-2">\
                                <input id="user-'+v.username+'-switch-'+qid+'" type="checkbox" class="js-switch js-check-change"/>\
                            </div>\
                        </div>'

                dataswitches.push("#user-"+v.username+"-switch-"+qid);
            });

            expert.innerHTML = cont
            $("#ExpertContainter").append(expert);

            $.each(dataswitches, function(i,s){
                var elem = document.querySelector(s);
                var newSwitch = new Switchery(elem);
                switches.push(newSwitch);
            });
            
        }
    });

};

function removeExperts(qid){
// Remove the experts that for that question
    $("#" + qid + "-container").remove();

    var newSwitches = [];
    $.each(switches, function(i,s){

        var id = s.element.id.split("-")

        if(id.length != 4 | id[3] != qid){
            newSwitches.push(s);
        }

    })

    switches = newSwitches;
};

$(document).ready(function() {

	// 
    var elems = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));
    elems.forEach(function(html) {

        html.onchange = function(self){
            console.log(self)
            if(self.target.id.split("-")[0] == "question"){
                
                console.log(ischecked(self.target.id));

                if(ischecked(self.target.id)){
                    console.log("Display");
                    // Make a ajax call and add expert information 
                    displayExperts(self.target.id.split("-")[1])
                } else {
                    console.log("Remove");
                    removeExperts(self.target.id.split("-")[1])
                }
            }
        }
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
		"data": {"experts": expertList},
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
    
    console.log(switches);

	$.each(switches, function(i,v){
		if(v.element.id.split("-")[0] == "user" && v.element.checked){
            var id = v.element.id.split("-");
			expertList.push({"qid": id[3], "user":id[1]});
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
