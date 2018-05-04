var SWITCHES = [],
	TABDATA = {},
	TABCOUNTER = 0;

// Keep tab of active tab history
var ACTIVE = {};
ACTIVE.tabs = [];
ACTIVE.add = function (item) {
	var index = this.tabs.indexOf(item);
	// Remove item if it already exists
	if (index > -1) {
		this.tabs.splice(index, 1);
	}
	this.tabs.push(item);
};
ACTIVE.last = function () {
	return this.tabs[this.tabs.length - 1];
};

// Default map settings
var PROJECTION = 'EPSG:4326', // World Geodetic System
	ZOOM = 2.2,
	LON = 0,
	LAT = 0;

function initialiseMap() {
	console.log("Initialising map...")
	var myView = new ol.View({
		center: [LON, LAT],
		zoom: ZOOM,
		enableRotation: false,
		enableZoom: false,
		extent: [LON, LAT,  // minx, miny
				 LON, LAT], // maxx, maxy
		projection: PROJECTION
	});

	var raster = new ol.layer.Tile({
		source: new ol.source.OSM()
	});

	var map = new ol.Map({
		view: myView,
		layers: [raster],
		target: 'map',
		controls: [], // Remove default controls (e.g. zoom buttons)
		interactions: [new ol.interaction.DragPan()] // Enable panning only
	});

	//map.setSize([1276,561]) // Restricting map height

	$('#map').data('map', map);
}

function newTab() {
	// Create new tab ID
	TABCOUNTER += 1;
	var id = "tab_" + TABCOUNTER;

	console.log("Creating new tab: " + id)

	// Create tab layer storage
	TABDATA[id] = {};

	// Create HTML tab
	$('<li><a id="'+id+'" href="#map-content" data-toggle="tab">New tab</a></li>').appendTo('#tabs');
	// Add listener
	$('#'+id).on('shown.bs.tab', function (e) {
		console.log("Tab show: " + e.target.id)
		// Update active tab list
		ACTIVE.add(e.target.id);
		// Get active vector layers for this tab
		layerCodes = Object.keys(TABDATA[e.target.id]);
		updateSwitches(layerCodes);
		updateMap();
	});
	// Make the new tab active
	$('#'+id).tab('show');

	// Create remove tab if it isn't already created and more than one map tab is present
	if ($('#removetab').length == 0 && Object.keys(TABDATA).length != 1) {
		// Create HTML
		$('<li id="removetab" class="pull-right"><a href="#map-content" data-toggle="tab" aria-expanded="false">Remove tab</a></li>').appendTo('#tabs');
		// Add listener
		$('#removetab').on('shown.bs.tab', function(e) {
			console.log("Removing tab: " + ACTIVE.last())
			delete TABDATA[ACTIVE.last()];
			$('#'+ACTIVE.tabs.pop()).remove();
			$('#'+ACTIVE.last()).tab('show');

			// Delete 'remove' tab if only one tab left
			if (Object.keys(TABDATA).length == 1) {
				$('#removetab').remove();
			}
		})
	}
}

function updateSwitches(layerCodes) {
	console.log("Updating switches: " + layerCodes)
	SWITCHES.forEach(function(html) {
		// Get ID code of switch
		var lcode = html.element.id.split("-")[0],
			isOn = false;
		layerCodes.forEach(function(code) {
			if (code == lcode) {
				isOn = true;
			}
		});

		setSwitchery(html, isOn);
	})
}

// Check or un-check a switch
function setSwitchery(switchElement, checked) {
    if((checked && !switchElement.isChecked()) || (!checked && switchElement.isChecked())) {
        switchElement.setPosition(true);
    }
}

function updateMap() {
	var map = $('#map').data('map'),
		layers = map.getLayers().getArray(),
		tab = ACTIVE.last();

	console.log("Updating map: " + Object.keys(TABDATA[tab]))

	// Add layers from TABDATA which aren't already on the map
	Object.keys(TABDATA[tab]).forEach(function(key) {
		var found = false;
		layers.forEach(function(layer) {
			if (TABDATA[tab][key] == layer) {
				found = true;
			}
		});
		if (found == false) {
			map.addLayer(TABDATA[tab][key]);
		}
	});

	// Remove layers which aren't in TABDATA
	var baseLayer = true, // Protect map layer
		layersToRemove = [];

	layers.forEach(function(layer) {
		if (baseLayer) {
			baseLayer = false;
			return;
		}

		var found = false;
		Object.keys(TABDATA[tab]).forEach(function(key) {
			if (TABDATA[tab][key] == layer) {
				found = true;
			}
		});
		if (found == false) {
			layer.getSource().forEachFeature(function(feature) {
				console.log(feature.weight)
			});
			layersToRemove.push(layer);
		}
	});

	// This is done after so that size of array is affect while looping
	layersToRemove.forEach(function(layer) {
		map.removeLayer(layer);
	});
}

function updateTabData(lcode, layer=null) {
	// Get active tab id
	var tab = ACTIVE.last();
	console.log("Updating tab data: " + tab)
	if (layer == null) { // Null layer: delete layer
		delete TABDATA[tab][lcode];
		// Avoid empty tab names
		if (Object.keys(TABDATA[tab]).length == 0) {
			document.getElementById(tab).innerHTML = "New tab";
			return;
		}
	} else {
		// Save new layer, keyed by layer code and current tab ID
		TABDATA[tab][lcode] = layer;
	}
	// Update tab name
	document.getElementById(tab).innerHTML = Object.keys(TABDATA[tab]);
}

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
		SWITCHES.push(switchery); // Save reference to switches so they can be manipulated later
		setSwitchery(switchery, false);
	});

	// Set up listeners for tab creation/removal
	$('#newtab').on('shown.bs.tab', function (e) {
		newTab();
	});

	// Set up listeners for layer togglers
	var elems = Array.prototype.slice.call(document.querySelectorAll('.js-check-change'));
	elems.forEach(function(elem) {
		elem.onchange = function() {
			console.log("Switch toggled...")
			var lid = elem.id.split("-"),
				lcode = lid[0],
				lindex = lid[1];

			if (!elem.checked) { // Element is selected (counterintuitive)
				updateTabData(lcode);
				updateMap();
			} else {
				// Update map source
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

				updateTabData(lcode, vector);
				updateMap();
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

	initialiseMap();
	newTab();
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

			if(status == "nocontent"){
				// No more models for that question ID - Refresh the page for new information
				location.reload();
				return;
			}

			$("#mid").val(data.mid);

			// Load new climate model
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
