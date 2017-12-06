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
					// TODO remove currently drawn map and draw new layer on map
					console.log(lcode, lindex);
					console.log(MODEL_KML)
				});
				// Make the new tab active
				$('#'+lcode).tab('show');
			}
		};
	});

	scoreCMO(null, null, null);
});

function scoreSubmit(){
	scoreCMO($("#mid").val(), $("#qid").val(), $("#modelScore").val());
};

function scoreCMO(mid, qid, score){
	$.ajax({
		"url": "/training_CMOData",
		"type": "POST",
		"contentType": "application/x-www-form-urlencoded",
		"data": {"mid": mid, "qid": qid, "score": score},
		"success": function(data, status){
			console.log(data);

			// Update question text
			$("#questionText").text(data.question);

			// Get handle on model.getkml()
			MODEL_KML = data.model;

			// Default tab pick (quick and dirty)
			$('#Soil-0').click();
			$('#default_collapse').click();
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