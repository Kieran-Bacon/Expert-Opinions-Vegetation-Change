var MODEL_KML = null;

$(document).ready(function() {
	// Select the element and convert it to a ion slider
	$("#modelScore").ionRangeSlider({
		"start":50,
		"min":0
	});

	// Find all switches and make them js fun time switchs
	var elems = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));
	elems.forEach(function(html) {
		var switchery = new Switchery(html);
		// All turned off by default
		setSwitchery(switchery, false);
	});

	// Drawing the map
	var mapZoom = 2.25
	var centerLon = 5.921332  // x
	var centerLat = 44.791232 // y
	var extentDegrees = 15
	var mapCenter = ol.proj.transform([centerLon, centerLat], 'EPSG:4326', 'EPSG:3857');
	// Can pan +- 15 degrees North or South
	var extent = ol.proj.transform([centerLon, centerLat + extentDegrees], 'EPSG:4326', 'EPSG:3857');
	var extentY = extent[1] - mapCenter[1]

	var myView = new ol.View({center: mapCenter,
							  zoom: mapZoom,
							  enableRotation: false,
							  enableZoom: false,
							  // [minx, miny, maxx, maxy]
							  extent: [mapCenter[0], mapCenter[1] - extentY,
									   mapCenter[0], mapCenter[1] + extentY]});

	var vector = new ol.layer.Heatmap({
		source: new ol.source.OSM()
	})

	var raster = new ol.layer.Tile({
        source: new ol.source.OSM()
    });

	var map = new ol.Map({
		view: myView,
		layers: [],
		//layers: [vector],
		// 	new ol.layer.Tile({
		// 		source: new ol.source.OSM()
		// 	})
		// ],
		target: 'map',
		controls: [], // Remove default controls (e.g. zoom buttons)
		interactions: [new ol.interaction.DragPan()] // Only enable panning
	});

	// Set up listeners
	var elems = Array.prototype.slice.call(document.querySelectorAll('.js-check-change'));
	elems.forEach(function(elem) {
		elem.onchange = function() {
			var lid = elem.id.split("-");
			var lcode = lid[0];
			var lindex = lid[1];
			if (!elem.checked) { // If element is not CURRENTLY checked
				$('#'+lcode).remove();
				// Show last tab
				$('#tabs a:last').tab('show');
			} else {
				// Create the tab
				$('<li id="'+lcode+'"><a href="#map-content" data-toggle="tab">'+lcode+'</a></li>').appendTo('#tabs');
				// On tab change listener
				$('#'+lcode).on('shown.bs.tab', function (e) {
					// Update map
					console.log(lcode);

					kmlLocation = "http://" + window.location.hostname + ":" + window.location.port + "/collect_model_kml/" + $("#mid").val() + "/" + lindex;
					console.log(kmlLocation);

					var vector = new ol.layer.Heatmap({
						source: new ol.source.Vector({
						  url: kmlLocation,
						  format: new ol.format.KML({
							extractStyles: false
						  })
						}),
						blur: 4,
						radius: 3
					  });
				
					  vector.getSource().on('addfeature', function(event) {
						// 2012_Earthquakes_Mag5.kml stores the magnitude of each earthquake in a
						// standards-violating <magnitude> tag in each Placemark.  We extract it from
						// the Placemark's name instead.
						var name = event.feature.get('name');
						var magnitude = parseFloat(name.substr(2));
						event.feature.set('weight', magnitude);
					  });
				
					  var raster = new ol.layer.Tile({
						source: new ol.source.Stamen({
						  layer: 'toner'
						})
					  });
				
					  $(".ol-viewport").remove();

					  var map = new ol.Map({
						layers: [raster, vector],
						target: 'map',
						view: new ol.View({
						  center: [0, 0],
						  zoom: 2
						})
					  });



				});
				// Make the new tab active
				$('#'+lcode).tab('show');
			}
		};
	});

	collectModel();
	$("#questionSelect").change(collectModel);
});

function collectModel(){

	var qid = $("#questionSelect option:selected").val();
	if( qid == null){ return; }

	$.ajax({
		"url": "/training/collectCMO",
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"qid": qid},
		"success": function(data, status){

			console.log(data);
			console.log(status);

			if(status == "nocontent"){
				// No more models for that question ID - Refresh the page for new information
				location.reload();
				return;
			}

			$("#mid").val(data.mid);

			// Get handle on model.getkml()
			MODEL_KML = data.model;

			// Default tab pick (bit ugly)
			$('#Soil-0').click();
			$('#default_collapse').click();

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
}

function scoreModel(){

	var qid = $("#questionSelect option:selected").val();
	var mid = $("#mid").val();
	var score = $("#modelScore").val();

	$.ajax({
		"url": "/training/scoreCMO",
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"qid": qid, "mid":mid, "score": score},
		"success": function(data, status){
			// Get next Model
			collectModel();
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
}

// Check or un-check a switch
function setSwitchery(switchElement, checked) {
    if((checked && !switchElement.isChecked()) || (!checked && switchElement.isChecked())) {
        switchElement.setPosition(true);
        switchElement.handleOnchange(true);
    }
}