$(document).ready( function(){
	// Select the element and convert it to a ion slider
	$("#modelScore").ionRangeSlider({
		"start":50,
		"min":0
	});

	// Find all switches and make them js fun time switchs
	var elems = Array.prototype.slice.call(document.querySelectorAll('.js-switch'));
	elems.forEach(function(html) {
		var switchery = new Switchery(html);
	});

	// TODO drawing the map here

	// Constraining map view
	//var myExtent = new ol.Extent([0,0,0,0])
	var myView = new ol.View({center: [0, 0],
							  zoom: 2,
							  enableRotation: false,
							  minZoom: 2,
							  // TODO use mapsize to properly constrain looking around
							  extent: [10,0,1000000,1000000]}); // Control how much looking around you can do
    var map = new ol.Map({
        view: myView,
        layers: [
            new ol.layer.Tile({
            source: new ol.source.OSM()
            })
        ],
		target: 'map',
		controls: [] // Remove default controls
	});
	
	console.log("hello")

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

			$("#questionText").text(data.question);
		}
	});
}