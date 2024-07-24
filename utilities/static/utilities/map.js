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

function marker_index_to_infos(index) {
    let infos = [];
    if (clustered_marker_indices.includes(index)) {
        // multiple locations are clustered together
        var elements = clustered_marker_dict[index].elements;
        for (let i=0; i < elements.length; i++) {
            var info = d[elements[i].options.index]; 
            infos.push(info);
        }
    } else {
        infos.push(d[index]);
    }
    return infos
}

function show_info(index) {
    // shows general information about a location
    var label = document.getElementById('city_label');
    var infos = marker_index_to_infos(index);
    var html = ''
    for (let i=0; i < infos.length; i++) {
        var info = infos[i]; 
        html += info.name
        html += '<small> (' + info.count + ')</small>'
        if (html.length > 140) {
            html += '<small> [...] + ' + (infos.length -1 -i)
            html += ' locations</small>'
            break;
        }
        if ( i != infos.length -1) {
            html += ', '
        }
    }
    label.innerHTML = html;
}

function toggle_right_sidebar_category(element) {
    //hide reveal category items (e.g. Text) from sidebar
    var dlinks = document.getElementById(element.dataset.links_id);
    console.log(dlinks,'dlinks',element,'element',element.dataset.links_id)
    if (dlinks.style.display == "") {
        element.style.color = element.data_color_inactive;//"grey";
        dlinks.style.display = "none";
    } else {
        element.style.color = element.data_color_active;//"#2f3030";
        dlinks.style.display = "";
    }
}

function info_to_categories(info) {
    var categories = {};
    for (let i=0; i < info.active_identifiers.length; i++) {
        var identifier = info.identifiers[i];
        var category_name = identifier.split('_')[1];
        if (!(category_name in categories)) {
            categories[category_name] = [];
        }
        categories[category_name].push(identifier);
    }
    return categories
}

function _add_instance(instance, category, category_div) {
    var dlinks = document.getElementById(category + '-links-' 
        + category_div.id);
    var line_div = document.createElement('div');
    line_div.classList.add('instance-line-div');
    dlinks.appendChild(line_div);
    var a = document.createElement('a');
    line_div.appendChild(a);
    a.setAttribute('href',instance.detail_url);
    a.innerHTML = instance.name;
    a.classList.add("small-text");
    a.classList.add("title-link");
    console.log(instance,'<---')
}

async function get_instances(identifiers, category, category_div) {
    var path = '/utilities/ajax_instance/';
    for (let i=0; i < identifiers.length; i++) {
        var identifier = identifiers[i];
        var url = path +  identifier.replaceAll('_','/');
        console.log(url,'url')
        const response = await fetch(url);
        var data = await response.json();
        _add_instance(data, category, category_div);
    }
}

function show_category(city_div, category, identifiers) {
    var count_active = identifiers.length;
    var category_div = document.createElement('div');
    category_div.id = category + '-all-' + city_div.id;
    city_div.appendChild(category_div);
    console.log(identifiers,'identifiers')
    var a = document.createElement('a');
    category_div.appendChild(a);
    var dlinks = document.createElement('div');
    dlinks.id = category + '-links-' + category_div.id;
    category_div.appendChild(dlinks);
    get_instances(identifiers, category, category_div);
    a.id = category + '_category-toggle_' + category_div.id
    a.setAttribute('href',"javascript:void(0)");
    a.setAttribute('onclick', 'toggle_sidebar_category(this)');
    a.setAttribute('data-links_id', dlinks.id);
    a.setAttribute('data-identifiers',identifiers);
    a.innerHTML = category + ' <small>(' + count_active + ')</small>';
    a.classList.add('category-header');
}

function show_categories(info) {
    var sidebar = document.getElementById('information');
    var city_div = document.createElement('div');
    sidebar.appendChild(city_div);
    city_div.id = info.pk + "-links";
    console.log(Object.entries(info),'show category')
    var categories = info_to_categories(info);
    for (const [category, identifiers] of Object.entries(categories)) {
        show_category(city_div, category, identifiers);
    }
    console.log(categories,'categories')
}

function show_city(info) {
    console.log('show city',info.name)
    var sidebar = document.getElementById('information');
    var div = document.createElement('div');
    sidebar.appendChild(div);
    var a = document.createElement('a');
    a.setAttribute('href','javascript:void(0)');
    a.setAttribute('onclick', 'toggle_right_sidebar_category(this)');
    a.setAttribute('data-links_id', info.pk + '-links');
    a.setAttribute('data-color_inactive', 'grey');
    a.setAttribute('data-color_active', '#2f3030');
    a.classList.add("city-header");
    var html = info.name + '<small> (' + info.count + ') </small>';
    a.innerHTML = html;
    div.appendChild(a);
    show_categories(info);
}

function clear_right_sidebar() {
    // clear the right sidebar
    var right_sidebar = document.getElementById('information');
    right_sidebar.innerHTML = '';
}

function show_right_sidebar(index) {
    clear_right_sidebar();
    var infos = marker_index_to_infos(index);
    console.log(infos,'infos')
    for (let i=0; i < infos.length; i++) {
        var info = infos[i]; 
        show_city(info);
    }
}

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
	//open_right_nav();
    console.log(this,'clicked')
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
	hide_markers();
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

function hide_markers() {
	//remove markers from map
	for (i = 0; i<all_markers.length; i++) {
		var marker = all_markers[i];
		marker.remove();
	}
}

function update_markers(markers) {
	// show markers on map;
	//apply clustering to markers (cluster overlapping markers together
	//filter out markers without any active ids
	show_markers(markers, true);
	[clustered_marker_dict, clustered_marker_indices]=cluster(markers)
	show_markers(markers, false);
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
	all_markers.push(marker)
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



function update_d() {
    console.log(filter_active_ids,'filter active ids')
    for (var i = 0; i<d.length; i++) {
        var item = d[i];
        //console.log(item)
        item.active_identifiers = [];
        for (var j = 0; j<item.identifiers.length; j++) {
            if (filter_active_ids.includes(item.identifiers[j])) {
                item.active_identifiers.push(item.identifiers[j]);
            }
        }
        item.active_count = item.active_identifiers.length;
        if (item.active_count == 0) {
            //console.log(item, d[i], 'not active')
        }
    }
}

function update_active_markers() {
    // update the active markers based on the active ids
    active_markers = [];
	for (var i = 0; i< all_markers.length; i++) {
		var marker = all_markers[i];
        var index = marker.options.index;
        if (d[index].active_count > 0) {
            active_markers.push(marker);
            //console.log(d[index].active_count,'active')
        }
        //console.log(d[index],marker,'updating',d[index].active_count)
    }
    window.active_markers = active_markers;
}

function update_map() {
    update_d();
    update_active_markers();
    show_markers(active_markers);
    active_markers.sort(sort_on_x);
    update_markers(active_markers);
    console.log('updated map')
}

// the d element contains all information linking locations to instances
var d= JSON.parse(document.getElementById('d').textContent);
var d = Object.values(d)
var all_markers = [];
for (var i = 0; i<d.length; i++) {
	make_circle_marker(d[i],i);
	//make_marker(d[i],i);
}
var active_markers = all_markers.slice();
var controlLayers;
var overlayMarkers= {};
var clustered_markers = [];
var clustered_marker_indices = [];
var clustered_marker_dict = {};
show_markers(active_markers);
active_markers.sort(sort_on_x);
update_markers(active_markers);

console.log(all_markers,'markers')
window.all_markers = all_markers;
window.active_markers = active_markers;
window.d = d;
window.clustered_marker_indices = clustered_marker_indices;
window.clustered_marker_dict = clustered_marker_dict;
window.toggle_right_sidebar_category = toggle_right_sidebar_category;
console.log(current_active_ids,'current active ids')
console.log(clustered_marker_dict,'clustered marker dict')
console.log(clustered_marker_indices,'clustered marker indices')

document.addEventListener('active_ids_update_event', update_map); 

mymap.on('zoomend', function() {
	// update the clustering after zooming in or out
	console.log('zoomed')
	update_map();
});
