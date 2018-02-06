switch_list = [];

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
		switch_list.push(switchery);
		setSwitchery(switchery, false);
	});

	// Drawing the map
	var mapZoom = 2.25
	var centerLon = 5.921332  // x
	var centerLat = 44.791232 // y
	var extentDegrees = 23
	var mapCenter = ol.proj.transform([centerLon, centerLat], 'EPSG:4326', 'EPSG:3857');
	// Can pan +- extentDegrees North or South
	var extent = ol.proj.transform([centerLon, centerLat + extentDegrees], 'EPSG:4326', 'EPSG:3857');
	var extentY = extent[1] - mapCenter[1]

	var myView = new ol.View({center: mapCenter,
							  zoom: mapZoom,
							  enableRotation: false,
							  enableZoom: false,
							  // [minx, miny, maxx, maxy]
							  extent: [mapCenter[0], mapCenter[1] - extentY,
									   mapCenter[0], mapCenter[1] + extentY],
							  projection:'EPSG:3857'});

	var vector = new ol.layer.Heatmap({
		source: new ol.source.OSM()
	});

	var raster = new ol.layer.Tile({
        source: new ol.source.OSM()
    });

	var map = new ol.Map({
		view: myView,
		layers: [raster, vector],
		target: 'map',
		controls: [], // Remove default controls (e.g. zoom buttons)
		interactions: [new ol.interaction.DragPan()]// new ol.interaction.MouseWheelZoom()] // Only enable panning
	});
	map.setSize([1276,561])
	$('#map').data('map', map);

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
					// Update map source
					var map = $('#map').data('map');

					kmlLocation = "http://" + window.location.hostname + ":" + window.location.port + "/collect_model_kml/" + $("#mid").val() + "/" + lindex;
					console.log(kmlLocation);

					sourceVector = new ol.source.Vector({
						url: kmlLocation,
						format: new ol.format.KML({
						  	extractStyles: false
						})
					});

					var vector = new ol.layer.Heatmap({
						source: sourceVector,
						blur: 3,
						radius: 5
					});

					var max = -1
					var min = 1
					vector.getSource().on('addfeature', function(event) {
						var name = event.feature.get('name');
						var weight = parseFloat(name.substr(1,name.length-2));

						if (weight > max) {
							max = weight
							console.log("Max:", max)
						}
						if (weight < min) {
							min = weight
							console.log("Min:", min)
						}

						event.feature.set('weight', weight);
					});

					vectorLayer = map.getLayers().getArray()[1];
					map.removeLayer(vectorLayer);
					map.addLayer(vector);
				});
				// Make the new tab active
				$('#'+lcode).tab('show');
			}
		};
	});

	// Add colorbar
	var cbar  = document.getElementById('cbar'),
    	ctx = cbar.getContext('2d');

	for(var i = 0; i <= 255; i++) { // fill strokes
    	ctx.beginPath();

    	var color = 'rgb(' + i + ', ' + (255 - i) + ', 0)';
    	ctx.fillStyle = color;

    	ctx.fillRect(i, 0, 1, 20);
	}
	$('#colorbar').offset().top;

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
			$("#mid").val(data.mid);
			$("#qid").val(data.qid);
			$("#questionText").text(data.question);

			// Default tab pick (quick and dirty)
			tabReset()
			$('#Soil-15').click();
			$('#default_collapse').click();
		},
		"error": function(data, status){
			console.log(data);
			console.log(status);
			// TODO: Change the path name if and only if status is 303
			window.location.pathname = "/all_labelled_screen";
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

function tabReset() {
	switch_list.forEach(function(html) {
		// All turned off by default
		if (html.isChecked()) {
			$('#' + html.element.id).click();
		}
	});
}