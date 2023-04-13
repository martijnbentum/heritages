import {cluster, sort_on_x} from './cluster.js';

// leaflet map setup
var mymap = L.map('mapid').setView([52.0055328,4.67565177],5);
var attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">'
attribution += 'OpenStreetMap contributors &copy; '
attribution += '<a href="https://carto.com/attribution">CARTO</a>'
const tileUrl = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
const tiles = L.tileLayer(tileUrl,{attribution});
tiles.addTo(mymap);


var marker_color = '#0d2a59'
var highlight_color = "#4985e6"
var click_color = "#db1304"
var html_icon = '<a style="color:'+marker_color
html_icon +=';"><i class="fas fa-map-marker-alt"></i></i></a>'
var html_highlight_icon = '<a style="color:'+highlight_color
html_highlight_icon+=';"><i class="fas fa-map-marker-alt"></i></i></a>'
var last_clicked_marker = false;
var last_activated = false;
var last_deactivated = false;
var entries = [];

function on_marker_hover(e) {
	//show info and change color of an element on the map when hovered
	deactivate_marker(last_activated);
	activate_marker(this);
	show_info(this.options.index);
}

function on_marker_leave(e) {
	//nothing to do now
}

function on_marker_click(e) {
	// opens sidebar (if closed) removes old elements (if present) 
	// shows instances linked to location in sidebar
	var s = this.options.className;
	set_marker_clicked(this)
	show_right_sidebar(this.options.index);
	open_right_nav();
}

function activate_marker(marker) {
	//change the color of a marker to highlight when hovered
	if (marker == last_clicked_marker) { return false}
	try {marker.setStyle({fillColor:highlight_color, color:highlight_color});}
	catch {marker._icon.innerHTML = html_highlight_icon;}
	last_activated = marker;
}
	
function deactivate_marker(marker) {
	//change the color of a marker to default when hovered
	if (marker == last_clicked_marker) { return false}
	if (last_activated == false) { return false }
	try {marker.setStyle({fillColor:marker_color,color:marker_color});}
	catch {marker._icon.innerHTML = html_icon;}
	last_deactivated = marker;
}

function set_marker_clicked(marker) {
	// change color of marker to clicked color
	set_marker_unclicked();
	try {marker.setStyle({fillColor:click_color, color:click_color});}
	catch {marker._icon.innerHTML = html_highlight_icon;}
	last_clicked_marker = marker;
}

function set_marker_unclicked() {
	// change color of marker to default color
	if (last_clicked_marker == false) { return false }
	var marker = last_clicked_marker;
	try {marker.setStyle({fillColor:marker_color,color:marker_color});}
	catch {marker._icon.innerHTML = html_icon;}
	last_clicked_marker = false
}

function add_marker_behavior(marker) {
	// adds marker behavior
	marker.on('mouseover',on_marker_hover)
	marker.on('mouseout',on_marker_leave)
	marker.on('click',on_marker_click)
}


function show_markers(markers, make_point = true) {
	//var controlLayers;
	hide_markers(layerDict['circle']);
	for (i = 0; i<markers.length; i++) {
		var marker = markers[i];
		if (make_point) {
			marker.addTo(mymap);
		} else if ( clustered_marker_indices.includes(marker.options.index) ) {
			if (clustered_marker_dict[marker.options.index].plotted) {
				continue;
			}
			clustered_marker_dict[marker.options.index].center_element.addTo(mymap);
			clustered_marker_dict[marker.options.index].plotted = true;
		} else {
			marker.addTo(mymap);
		}
	}
}

function hide_markers(markers) {
	//remove markers from map
	for (i = 0; i<markers.length; i++) {
		var marker = markers[i];
		marker.remove();
	}
}

function update_markers() {
	// show markers on map;
	//apply clustering to markers (cluster overlapping markers together
	//filter out markers without any active ids
	show_markers(active_markers, true);
	[clustered_marker_dict, clustered_marker_indices] = cluster(active_markers)
	show_markers(active_markers, false);
}

function make_circle_marker(loc,i) {
	//create a marker a circle
	var latlng = loc2latlng(loc);
	if (latlng == false) { return false;}
	name = loc.name
	var marker=L.circleMarker(latlng,{color:marker_color,weight:2,
		fillOpacity:0.3,
		className:loc.name, index:i,visible:'active'})
	var radius = 4;
	marker.setRadius(radius)
	add_marker_behavior(marker);
	layerDict['circle'].push(marker)
	//marker.addTo(mymap);
	return marker;
}

function loc2latlng(loc) {
	//extract latitude and longitude form loc object
	try { var latlng = loc.gps.split(',').map(Number); }
	catch {var latlng = [] }
	if (latlng.length != 2) {
		return false
	}
	if (typeof(latlng[0]) != 'number' || typeof(latlng[1]) != 'number') {
		return false
	}
	return latlng
	}

function collect_active_markers() {

}

var names = 'circle,other'.split(',');
var layerDict = {}
for (var i = 0; i<names.length; i++) {
	layerDict[names[i]] = []
}

// the d element contains all information linking locations to instances
var d= JSON.parse(document.getElementById('d').textContent);
var d = Object.values(d)
for (i = 0; i<d.length; i++) {
	make_circle_marker(d[i],i);
	//make_marker(d[i],i);
}

var controlLayers;
var overlayMarkers= {};
var clustered_markers = [];
var clustered_marker_indices = [];
var clustered_marker_dict = {};
var active_markers = [];
var active_markers = [...layerDict['circle']];
show_markers(active_markers);
active_markers.sort(sort_on_x);
update_markers(active_markers);

mymap.on('zoomend', function() {
	// update the clustering after zooming in or out
	console.log('zoomed')
	update_markers();
});
