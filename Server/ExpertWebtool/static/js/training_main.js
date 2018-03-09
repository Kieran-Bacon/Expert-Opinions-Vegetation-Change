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

	var destination_proj = 'EPSG:4326';	// World Geodetic System

	// Default map settings
	var defaultZoom = 2.01,
		defaultLon = 0,
		defaultLat = 0;

	var myView = new ol.View({center: [defaultLon, defaultLat],
							  zoom: defaultZoom,
							  enableRotation: false,
							  enableZoom: false,
							  // [minx, miny, maxx, maxy]
							  extent: [defaultLon, defaultLat,
									   defaultLon, defaultLat],
							  projection: destination_proj});

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
		interactions: [new ol.interaction.DragPan()] // Enable panning only
	});

	//map.setSize([1276,561]) // Restricting map height

	$('#map').data('map', map);

	// Set up listeners
	var elems = Array.prototype.slice.call(document.querySelectorAll('.js-check-change'));
	elems.forEach(function(elem) {
		elem.onchange = function() {
			var lid = elem.id.split("-"),
				lcode = lid[0],
				lindex = lid[1];

			// If element is not CURRENTLY checked, show last tab
			if (!elem.checked) {
				$('#'+lcode).remove();
				$('#tabs a:last').tab('show');
			} else {
				// Create the tab
				$('<li id="'+lcode+'"><a href="#map-content" data-toggle="tab">'+lcode+'</a></li>').appendTo('#tabs');
				// On tab change listener
				$('#'+lcode).on('shown.bs.tab', function (e) {
					// Update map source
					var map = $('#map').data('map');

					kmlLocation = "http://" + window.location.hostname + ":" + window.location.port + "/collect_model_kml/" + $("#mid").val() + "/" + lindex;

					sourceVector = new ol.source.Vector({
						url: kmlLocation,
						format: new ol.format.KML({
						  	extractStyles: false
						})
					});

					var vector = new ol.layer.Heatmap({
						source: sourceVector,
						blur: 10,
						radius: 6
					});

					vector.getSource().on('addfeature', function(event) {
						var name = event.feature.get('name');
						var weight = parseFloat(name.substr(1,name.length-2));

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
			tabReset()
			$('#Soil-15').click();
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

function tabReset() {
	switch_list.forEach(function(html) {
		// All turned off by default
		if (html.isChecked()) {
			$('#' + html.element.id).click();
		}
	});
}