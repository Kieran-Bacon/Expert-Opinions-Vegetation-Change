/**
 * The training page browser side functionality.
 * 
 * @author Paul Kim
 */

// ---------------------------------------------------------------------

// LAYER SWITCHES
var SWITCHES = [];

/**
 * Set a switch to on/off if it is not already in the correct state.
 * 
 * @param {Object}  switchElement The HTML switch element.
 * @param {Boolean} checked       The desired state of the switch.
 */
function setSwitchery(switchElement, checked) {
    if((checked && !switchElement.isChecked()) || (!checked && switchElement.isChecked())) {
        switchElement.setPosition(true);
    }
}

/**
 * Initialise layer switches by creating Switchery elements and setting
 * up switch listeners.
 */
function initialiseSwitches() {
	// Get switch HTML elements
	var elements = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));
	elements.forEach(function(element) {
		var switchery = new Switchery(element);
		SWITCHES.push(switchery);
		// Toggle switches off by default
		setSwitchery(switchery, false);
	});

	// Set up listeners for switches
	elements = Array.prototype.slice.call(document.querySelectorAll('.js-check-change'));
	elements.forEach(function(element) {
		element.onchange = function() {
			var switchID = element.id.split("-"),
				layerCode = switchID[0],
				layerIndex = switchID[1];

			////console.log("Switch toggled: ", layerCode);

			// If checked is true then switch is now on i.e. has been turned on
			activeTabID = ACTIVE.getActiveTab();
			LAYER_STORAGE.getLayerAndUpdateMap(activeTabID, layerIndex, element.checked);
			TAB_DATA.updateLayerCodes(activeTabID, layerCode, element.checked);
		}
	});
}

/**
 * Update layer switches according to given layer codes. Ensure
 * codes given are turned on and all others are turned off.
 * 
 * @param {Array} layerCodes Which layer switches should be on.
 */
function updateSwitches(layerCodes) {
	////console.log("Updating switches: " + layerCodes)

	// For each switch, check it is in layerCodes
	SWITCHES.forEach(function (html) {
		var switchCode = html.element.id.split("-")[0],
			turnOn = false;
		layerCodes.forEach(function(layerCode) {
			if (layerCode == switchCode) {
				turnOn = true;
			}
		});
		setSwitchery(html, turnOn);
	})
}

// ---------------------------------------------------------------------

// ACTIVE TAB TRACKING
var ACTIVE = {};
// Use a stack system to keep track of tab history
ACTIVE.tabs = [];

/**
 * Return the ID of the currently active tab without removing it from
 * the stack.
 * 
 * @return The ID of the currently active tab.
 */
ACTIVE.getActiveTab = function () {
	return this.tabs[this.tabs.length - 1];
};

/**
 * Set the active tab. If the tab already exists in the stack, remove it
 * and push it to the top of the stack.
 * 
 * @param {String} activeTab The active tab ID.
 */
ACTIVE.setActiveTab = function (activeTab) {
	var index = this.tabs.indexOf(activeTab);
	// Remove tab ID if it already exists in stack
	if (index > -1) {
		this.tabs.splice(index, 1);
	}
	this.tabs.push(activeTab);
};

/**
 * Delete the currently active tab (top of the stack) from the DOM. Show
 * the new active tab.
 */
ACTIVE.removeActiveTab = function () {
	$('#'+ACTIVE.tabs.pop()).remove();
	$('#'+ACTIVE.getActiveTab()).tab('show');
}

// ---------------------------------------------------------------------

// MODEL LAYER CACHING
var LAYER_STORAGE = {};

/**
 * Fetch a layer from storage and call map update functions. If the
 * layer is not in storage, it is loaded from the server. Once a layer
 * is loaded, the map is updated.
 * 
 * @param {String} tabID      The ID of the active tab.
 * @param {String} layerIndex The index of the layer to get.
 * @param {Boolean} toAdd     A flag whether to add/remove the layer.
 */
LAYER_STORAGE.getLayerAndUpdateMap = function (tabID, layerIndex, toAdd) {
	////console.log("Getting layer '" + layerIndex + "' for: " + tabID);

	// If layer is not in storage, load it
	if (!(layerIndex in LAYER_STORAGE)) {
		// Model layer data location
		url = "http://" + window.location.hostname + ":" + window.location.port;
		url += "/collect_model_kml/" + $("#mid").val() + "/" + layerIndex;
		////console.log("Fetching model layer from: " + url);

		LAYER_STORAGE[layerIndex] = {};
		$.getJSON(url).done(function(data) {
			// Expecting a GeoJSON feature collection
			data.features.forEach(function(feature){
				var lat = feature.geometry.coordinates[0],
					lon = feature.geometry.coordinates[1],
					featureKey = lat.toString() + "#" + lon.toString();

				// Store each point weight using the lat/lon as a key
				LAYER_STORAGE[layerIndex][featureKey] = feature.properties.weight;
			});
			// Add this to callback so that it is done only after layer is stored
			TAB_DATA.updateMapData(tabID, LAYER_STORAGE[layerIndex], toAdd);
			generateVectorSourceAndUpdate(tabID);
		});
	} else {
		TAB_DATA.updateMapData(tabID, LAYER_STORAGE[layerIndex], toAdd);
		generateVectorSourceAndUpdate(tabID);
	}
}

/**
 * Fetch a layer from storage and call map update functions. If the
 * layer is not in storage, it is loaded from the server. Once a layer
 * is loaded, only tab data is updated.
 * 
 * @param {String} tabID      The ID of the active tab.
 * @param {String} layerIndex The index of the layer to get.
 * @param {Boolean} toAdd     A flag whether to add/remove the layer.
 */
LAYER_STORAGE.getLayer = function (tabID, layerIndex, toAdd) {
	////console.log("Getting layer '" + layerIndex + "' for: " + tabID);

	// If layer is not in storage, load it
	if (!(layerIndex in LAYER_STORAGE)) {
		// Model layer data location
		url = "http://" + window.location.hostname + ":" + window.location.port;
		url += "/collect_model_kml/" + $("#mid").val() + "/" + layerIndex;
		////console.log("Fetching model layer from: " + url);

		LAYER_STORAGE[layerIndex] = {};
		$.getJSON(url).done(function(data) {
			// Expecting a GeoJSON feature collection
			data.features.forEach(function(feature){
				var lat = feature.geometry.coordinates[0],
					lon = feature.geometry.coordinates[1],
					featureKey = lat.toString() + "#" + lon.toString();

				// Store each point weight using the lat/lon as a key
				LAYER_STORAGE[layerIndex][featureKey] = feature.properties.weight;
			});
			// Add this to callback so that it is done only after layer is stored
			TAB_DATA.updateMapData(tabID, LAYER_STORAGE[layerIndex], toAdd);
			generateSourceVector(tabID);
			var activeTabID = ACTIVE.getActiveTab();
			if (activeTabID == tabID) {
				$('#dummytab').tab('show');
				$('#'+tabID).tab('show');
			}
		});
	} else {
		TAB_DATA.updateMapData(tabID, LAYER_STORAGE[layerIndex], toAdd);
		generateSourceVector(tabID);
		var activeTabID = ACTIVE.getActiveTab();
		if (activeTabID == tabID) {
			$('#'+tabID).tab('show');
		}
	}
}

/**
 * Clear layer storage (but keep functions).
 */
LAYER_STORAGE.clearStorage = function () {
	Object.keys(LAYER_STORAGE).forEach(function (key) {
		if (key != "clearStorage" && key != "getLayerAndUpdateMap" && key != "getLayer") {
			delete LAYER_STORAGE[key];
		}
	});
}

// ---------------------------------------------------------------------

// MAP VECTOR SOURCE CACHING
var VECTOR_SOURCE_STORAGE = {};

/**
 * Generate a vector layer for a given tab.
 * 
 * @param {String} tabID  The id of the active tab.
 * @param {Boolean} write Whether to generate or load a cached layer.
 */
function generateVectorSourceAndUpdate(tabID, write=true) {
	//console.log("Generating vector source for: " + tabID);

	var map = $('#map').data('map');

	if (write) {
		var vectorSource = new ol.source.Vector({});

		vectorSource.on("addfeature", function (event) {
			event.feature.set('weight', event.feature.P.weight)
		});

		Object.keys(TAB_DATA.mapData[tabID]).forEach(function (key) {
			var keySplit = key.split("#"),
				lat = keySplit[0],
				lon = keySplit[1];

			var	pointGeometry = new ol.geom.Point([lat,lon]);

			var pointFeature = new ol.Feature({
				geometry: pointGeometry,
				weight: TAB_DATA.mapData[tabID][key]
			});

			vectorSource.addFeature(pointFeature);
		});

		var modelLayer = new ol.layer.Heatmap({
			source: vectorSource,
			blur: 10,
			radius: 6
		});

		map.getLayers().getArray()[1].setSource(vectorSource);
		VECTOR_SOURCE_STORAGE[tabID] = vectorSource;
	} else {
		//console.log("Using cached source vector.")
		map.getLayers().getArray()[1].setSource(VECTOR_SOURCE_STORAGE[tabID]);
	}
	//console.log("Map updated.")
}

function generateSourceVector(tabID) {
	//console.log("Generating vector source for: " + tabID);

	var vectorSource = new ol.source.Vector({});

	vectorSource.on("addfeature", function (event) {
		event.feature.set('weight', event.feature.P.weight)
	});

	Object.keys(TAB_DATA.mapData[tabID]).forEach(function (key) {
		var keySplit = key.split("#"),
			lat = keySplit[0],
			lon = keySplit[1];

		var	pointGeometry = new ol.geom.Point([lat,lon]);

		var pointFeature = new ol.Feature({
			geometry: pointGeometry,
			weight: TAB_DATA.mapData[tabID][key]
		});

		vectorSource.addFeature(pointFeature);
	});

	var modelLayer = new ol.layer.Heatmap({
		source: vectorSource,
		blur: 10,
		radius: 6
	});

	VECTOR_SOURCE_STORAGE[tabID] = vectorSource;
}

VECTOR_SOURCE_STORAGE.clearStorage = function () {
	Object.keys(VECTOR_SOURCE_STORAGE).forEach(function (key) {
		if (key != "clearStorage") {
			//console.log(key)
			delete VECTOR_SOURCE_STORAGE[key];
		}
	});
}

// ---------------------------------------------------------------------

// TAB DATA MANAGEMENT
var TAB_DATA = {};
TAB_DATA.id_counter = 0;
TAB_DATA.n_tabs = 0;
TAB_DATA.layerCodes = {}; // Layer codes for each tab
TAB_DATA.mapData = {};    // Map layer data for each tab

/**
 * Generate a new and unique tab ID.
 * 
 * @return A new tab ID of the form "tab_n" where n is an integer.
 * @private
 */
TAB_DATA.newTabID = function () {
	TAB_DATA.id_counter += 1;
	return "tab_" + TAB_DATA.id_counter;
}

/**
 * Remove data of a given tab and update the state of TAB_DATA.
 * 
 * @param {String} tabID The ID of the tab data to remove
 * @private
 */
TAB_DATA.removeTabData = function (tabID) {
	delete TAB_DATA.layerCodes[tabID];
	delete TAB_DATA.mapData[tabID];
	TAB_DATA.n_tabs -= 1;
}

/**
 * The callback function fired when a tab is shown.
 * 
 * @param {Object} event The event fired, expects on shown.
 */
function tabShownListener(event) {
	//console.log("Tab show: " + event.target.id);

	var tabID = event.target.id;
	// Update active tab list
	ACTIVE.setActiveTab(tabID);
	// Get layer codes for active tab
	updateSwitches(TAB_DATA.layerCodes[tabID]);
	generateVectorSourceAndUpdate(tabID, write=false);
}

/**
 * The callback function fired when the remove tab 'button' is pressed.
 * 
 * @param {Object} event The event fired, expects on shown.
 */
function removeTabListener(event) {
	//console.log("Removing tab: " + ACTIVE.getActiveTab());

	TAB_DATA.removeTabData(ACTIVE.getActiveTab());
	ACTIVE.removeActiveTab();
	// Delete 'remove' tab if only one tab left
	if (TAB_DATA.n_tabs == 1) {
		$('#removetab').remove();
	}
}

/**
 * Generate HTML to create and remove new tabs interactively.
 */
TAB_DATA.newTab = function () {
	var tabID = this.newTabID();

	//console.log("Creating new tab: " + tabID)

	this.n_tabs += 1;
	// Create tab data storage
	this.layerCodes[tabID] = [];
	this.mapData[tabID] = {};

	// Create HTML tab
	$('<li><a id="'+tabID+'" href="#map-content" data-toggle="tab">New tab</a></li>').appendTo('#tabs');
	$('#'+tabID).on('shown.bs.tab', tabShownListener);
	$('#'+tabID).tab('show'); // Make the new tab active

	// Create remove tab if it isn't already created and more than one map tab is present
	if ($('#removetab').length == 0 && this.n_tabs != 1) {
		// Create HTML
		$('<li id="removetab" class="pull-right"><a href="#map-content" data-toggle="tab" aria-expanded="false">Remove tab</a></li>').appendTo('#tabs');
		$('#removetab').on('shown.bs.tab', removeTabListener);
	}
}

/**
 * Update a tab name in the DOM.
 * 
 * @param {String} tabID     The ID of the tab to update.
 * @param {String} layerCode The code to add/remove.
 * @param {Boolean} add      A flag to determine whether to add/remove.
 */
TAB_DATA.updateLayerCodes = function (tabID, layerCode, add) {
	//console.log("Updating tab layer codes for : " + tabID);

	// Update tab layer code data
	if (add) {
		this.layerCodes[tabID].push(layerCode);
	} else {
		var index = this.layerCodes[tabID].indexOf(layerCode);
		if (index > -1) {
  			this.layerCodes[tabID].splice(index, 1);
		}
	}
	// Update DOM
	if (TAB_DATA.layerCodes[tabID].length == 0) {
		document.getElementById(tabID).innerHTML = "New tab";
	} else {
		document.getElementById(tabID).innerHTML = TAB_DATA.layerCodes[tabID];
	}
}

/**
 * Update the map layer data for the given tab.
 * 
 * @param {String} tabID The ID of the active tab.
 * @param {Object} layer The layer data for updating.
 * @param {Boolean} add  A flag whether to add/remove the layer.
 */
TAB_DATA.updateMapData = function (tabID, layer, add) {
	//console.log("Updating map data for: " + tabID);

	if (TAB_DATA.mapData[tabID] == undefined) {
		TAB_DATA.mapData[tabID] = {};
	}

	Object.keys(layer).forEach(function (key) {
		if (add) {
			if (key in TAB_DATA.mapData[tabID]) {
				// If key already exists in map data, add it to existing value
				TAB_DATA.mapData[tabID][key] = TAB_DATA.mapData[tabID][key] + layer[key];
			} else {
				// Else create new entry in map data
				TAB_DATA.mapData[tabID][key] = layer[key];
			}
		} else {
			if (key in TAB_DATA.mapData[tabID]) {
				TAB_DATA.mapData[tabID][key] = TAB_DATA.mapData[tabID][key] - layer[key];
			}
		}
	});
}

// ---------------------------------------------------------------------

// MAP MANAGEMENT
// Default map settings
var PROJECTION = 'EPSG:4326', // World Geodetic System
	ZOOM = 2.2,
	LON = 0,
	LAT = 0;

/**
 * Initialise an OpenLayers map and assign it to the map DOM element.
 */
function initialiseMap() {
	//console.log("Initialising map...")
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

	var modelLayer = new ol.layer.Heatmap({
		blur: 10,
		radius: 6
	});

	var map = new ol.Map({
		view: myView,
		layers: [raster, modelLayer],
		target: 'map',
		controls: [], // Remove default controls (e.g. zoom buttons)
		interactions: [new ol.interaction.DragPan()] // Enable panning only
	});

	//map.setSize([1276,561]) // Restricting map height

	$('#map').data('map', map);
}

// ---------------------------------------------------------------------

// PAGE MANAGEMENT

/**
 * The document on ready function.
 */
function documentReady() {
	// Select the element and convert it to a ion slider
	$("#modelScore").ionRangeSlider({
		"start":50,
		"min":0
	});

	initialiseSwitches();

	// Set up listeners for tab creation/removal
	$('#newtab').on('shown.bs.tab', function (e) {
		TAB_DATA.newTab();
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
	TAB_DATA.newTab();
	collectModel();
	$("#questionSelect").change(collectModel);
}

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

			refresh();
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

function refresh() {
	//console.log("Refreshing model");
	// Clear vector source and model layer caches
	VECTOR_SOURCE_STORAGE.clearStorage();
	LAYER_STORAGE.clearStorage();
	TAB_DATA.mapData = {};

	ACTIVE.tabs.forEach(function (tabID) {
		elements = Array.prototype.slice.call(document.querySelectorAll('.js-check-change'));
		elements.forEach(function(element) {
			var switchID = element.id.split("-"),
				layerCode = switchID[0],
				layerIndex = switchID[1];
			var index = TAB_DATA.layerCodes[tabID].indexOf(layerCode);
			// Remove tab ID if it already exists in stack
			if (index > -1) {
				//console.log("Updating for code: " + layerCode)
				LAYER_STORAGE.getLayer(tabID, layerIndex, true);
			}
		});
	});
}

// ---------------------------------------------------------------------

$(document).ready(documentReady);