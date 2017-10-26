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
});