var us= JSON.parse(document.getElementById('usjs').textContent);
var date_range= JSON.parse(document.getElementById('date_range').textContent);
var found_tiles = document.getElementsByClassName('tile-item');
var found_rows = document.getElementsByClassName('row-item');
var count_dict = {};
var id_dict= JSON.parse(document.getElementById('id-dict').textContent);
var id_year_range_dict= JSON.parse(document.getElementById('id-year-range-dict').textContent);
var active_ids = id_dict['all']
var date_slider_active_ids = Object.keys(id_year_range_dict)
var temp =document.getElementById('filter-active-dict').textContent;
var filter_active_dict = JSON.parse(temp);
var sidebar_state = 'closed';
var btn = document.getElementById("togglebtn")
document.getElementById("content").style.marginLeft = "25px";
var combine = document.getElementById('combine')
var exact = document.getElementById('exact')
var selected_filters = [];
var new_query = 'false';
var century_set_date_slider = false;
var current_active_ids_set = id_dict['all']
	
toggle_sidebar();
window.onbeforeunload = function(){send_data();};


function set_new_query() {
	new_query = 'true';
}

function set_new_view_type() {
	if (view_type == 'tile_view') {
		view_type = 'row_view'
	} else {
		view_type = 'tile_view'
	}
}

function send_data() {
	const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
	var output = {};
	output['active_ids']=active_ids
	output['filters']=selected_filters
	output['query'] = get_query();
	output['time'] = Date.now()/1000;
	output['sorting_direction'] = get_sorting_direction();
	output['sorting_category'] = get_sorting_category();
	output['current_instance'] = clicked_instance;
	output['view_type'] = view_type;
	output['filter_active_dict'] = filter_active_dict;
	output['new_query'] = new_query;
	var d = new FormData();
	var blob = new Blob([JSON.stringify(output)],{type:'application/json'})
	d.append('file',blob,'active_ids.txt')
	var client = new XMLHttpRequest();
	client.open('post','/utilities/get_user_search_requests/');
	client.setRequestHeader("X-CSRFToken", csrftoken);
	client.send(d);
}



function update_hide_show_instances() {
	// hide or show instances based on active_ids array
	_update_instances(found_tiles);
	_update_instances(found_rows);
}

function _update_instances(items) {
	// helper function to hide & show instances for both tile and row view
	if (items.length == 0) {return}
	current_active_ids_set = [];
	for (let i=0;i<items.length;i++) {
		item = items[i]
		if (active_ids.includes(item.id) && date_slider_active_ids.includes(item.id)) {
			item.style.display = "";
			current_active_ids_set.push(item.id);
		} else {
			item.style.display = "none"
		}
	}
	console.log('cais',current_active_ids_set);
}

function toggle_filters_visibile(name) {
	var filter_set = document.getElementById(name+'-filters');
	var filter_name = document.getElementById(name+'-filter');
	if (filter_set.style.display == "") {
		filter_set.style.display = 'none';
		filter_name.style.color = 'lightgrey';
	} else {
		filter_set.style.display = '';
		filter_name.style.color = '#585e66';
	}

}

function update_sidebar() {
	//update the filters in the sidebar to show the current state
	var fad_keys = Object.keys(filter_active_dict);
	for (let i=0;i<fad_keys.length;i++) {
		var key = fad_keys[i];
		var filter_btn= document.getElementById(key)
		if (!filter_btn) {continue;}
		var [category_name,filter_name] = key.split(',');
		var updated = false
		var display_active = count_dict[key]['display_active']
		var active = count_dict[key]['active']
		var inactive = count_dict[key]['inactive']
		var filtered_inactive = count_dict[key]['filtered_inactive']
		var t = filter_btn.innerText;
		if (filter_active_dict[category_name] == 'active') {
			if (active == 0) {
					filter_btn.style.color='#bec4cf';
					updated = true;
					r = '(0)';
					filter_btn.style.display='none';
			}
			else { 
				r = '('+display_active+')';
				filter_btn.style.color='black'; 
				updated = true;
				filter_btn.style.display='';
			}
			filter_btn.innerText= t.replace(/\(.*\)/,r);
		}
		//console.log(key,selected_filters,333, filter_btn)
		// mark selected filters with a dot
		var t = filter_btn.innerText;
		if (selected_filters.includes(key)) {
			if (!t.includes('•')) {
				filter_btn.innerText= '•' + t;
			}	
		}
		else { 
			filter_btn.innerText= t.replace('•','');
		}
		if (updated) {continue;}

		var t = filter_btn.innerText;
		if (filter_active_dict[key] == 'active' && filter_btn) {
			r = '('+display_active+')';
			filter_btn.style.color='black';
		}
		if (filter_active_dict[key] == 'inactive' && filter_btn) {
			//this should take into account filters from other categories
			r = '('+filtered_inactive+')';
			filter_btn.style.color='#bec4cf';
			if (filtered_inactive == 0) {filter_btn.style.display='none';}
			else {filter_btn.style.display='';}
		}
		filter_btn.innerText= t.replace(/\(.*\)/,r);
	}
}


function set_filter_active_dict(active=NaN, inactive=NaN,category_name=NaN) {
	var d_keys = Object.keys(filter_active_dict);
	var active_count=0 
	var inactive_count=0 ;
	for (let i=0;i<d_keys.length;i++) {
		var key = d_keys[i];
		if (key.includes(active)) {
			filter_active_dict[key] = 'active';
		}
		else if (key.includes(inactive)) {
			filter_active_dict[key] = 'inactive';
		}
		// count the number of active filters in a category
		if (key.includes(category_name) && key != category_name) {
			if (filter_active_dict[key] == 'active') {active_count ++;}
			if (filter_active_dict[key] == 'inactive') {inactive_count ++;}
		}
	}
	//if there are no inactive filters in an category, the category is active
	if (inactive_count == 0){ filter_active_dict[category_name] = 'active'; }
	else if (active_count == 0) {
		//if there are no active filters, the last active filters is turned off
		//all filters in the category should be turned on
		set_filter_active_dict(active=category_name,
			inactive=NaN, category_name=category_name)
	}
	//there are one or more (but not all) filters active in a category
	//category is inactive
	else {filter_active_dict[category_name] = 'inactive'; }
	update_date_slider_to_century_filter();
}

function update_count_dict() {
	// count dict contains the active and non active instances for each filter
	// this is needed to update the state of the sidebar
	keys = Object.keys(filter_active_dict);
	count = 0;
	for (let i = 0;i<keys.length; i++) {
		key = keys[i]	
		var [category_name,filter_name] = key.split(',');
		if (category_name && filter_name) {
			var [da, active,inactive,f_inactive]=count_instances(category_name,filter_name);
			count_dict[key] =  {}
			count_dict[key]['display_active'] = da;
			count_dict[key]['active'] = active;
			count_dict[key]['inactive'] = inactive;
			count_dict[key]['filtered_inactive'] = f_inactive;
		}
	}
}

function get_ids_from_selected_filters_in_category(category) {
	//get all ids from selected filters in a category
	var category_ids = [];
	for (let i=0;i<selected_filters.length;i++) {
		var name= selected_filters[i];
		var [category_name,filter_name] = name.split(',');
		if (category != category_name) { continue; }
		var identifiers = id_dict[category_name][filter_name];
		category_ids.push(...identifiers);
	}
	return category_ids	
}

function update_active_ids() {
	var temp = [];
	if (selected_filters.length == 0) {
		active_ids = id_dict['all']
		return
	}
	category_names = Object.keys(id_dict);
	for (let i=0;i<category_names.length;i++) {
		var name= category_names[i];
		if (name == 'all') {continue;}
		var identifiers = get_ids_from_selected_filters_in_category(name)
		if (identifiers.length == 0) { continue; }
		temp.push(identifiers);
	}
	if (temp.length == 1) { active_ids = Array.from(...temp);}
	else {active_ids = intersection(temp);}
}

function update_selected_filters(name) {
	// the intersection of all instances linked to all selected filters
	// are the shown instances
	if (selected_filters.includes(name)) {
		selected_filters.splice(selected_filters.indexOf(name),1)
	}
	else {selected_filters.push(name); }
}

function toggle_filter(name) {
	//handles clicking a filter in the sidebar
	[category_name,filter_name] = name.split(',');
	if (filter_active_dict[category_name] == 'active') {
		//first filter term in a category is activated,
		//set all other terms 
		set_filter_active_dict(active=name, inactive=category_name, 
			category_name=category_name);
	}
	else if (filter_active_dict[name] == 'active') {
		//this filter name is active and possibly one ore other more filter names 
		//in this category are active
		set_filter_active_dict(active=NaN,inactive=name,category_name=category_name)
	}
	else {
		//current filter name is inactive, activate it and linked instances.
		set_filter_active_dict(active=name,inactive=NaN,category_name=category_name);
	}
	update_selected_filters(name);
	update_active_ids();
	update_hide_show_instances()
	update_count_dict();
	update_sidebar();
	set_nentries();
}

function intersection(array_of_arrays) {
	var data = array_of_arrays;
	var result = data.reduce( (a, b) => a.filter( c => b.includes(c) ) );
	return result 
}

function count_inactive_categories() {
	keys = Object.keys(id_dict);
	count = 0;
	for (let i = 0;i<keys.length; i++) {
		key = keys[i]	
		if (key == 'all') {continue;}
		if (filter_active_dict[key] == 'inactive') {
			count ++;
		}
	}
	return count
}

function make_ids_omiting_one_category(category) {
	var temp = [];
	category_names = Object.keys(id_dict);
	for (let i=0;i<category_names.length;i++) {
		var name= category_names[i];
		if (name == 'all' || category == name) {continue;}
		var identifiers = get_ids_from_selected_filters_in_category(name)
		if (identifiers.length == 0) { continue; }
		temp.push(identifiers);
	}
	if (temp.length == 0) { var ids = id_dict['all'];}
	else if (temp.length == 1) { var ids = Array.from(...temp);}
	else {ids = intersection(temp);}
	return ids
}
	

function count_instances(category_name,filter_name) {
	//count number of active and inactive instances in a category
	var identifiers = id_dict[category_name][filter_name];
	var display_active= count_array_overlap(current_active_ids_set,identifiers);
	var active= count_array_overlap(active_ids,identifiers);
	var inactive = identifiers.length - active;
	var ids = make_ids_omiting_one_category(category_name);
	var filtered_inactive = count_array_overlap(ids,identifiers);
	return [display_active, active, inactive,filtered_inactive]
}


function not_in_first_array(array1,array2) {
	//select all instance that are not in the first array
	var output = [];
	for (let i=0;i<array2.length;i++) {
		var item = array2[i];
		if (!array1.includes(item)) { output.push(item) }
	}
	return output;
}

function count_array_overlap(a1,a2) {
	//count the overlapping items from array 2 in array 1
	n= 0;
	for (let i=0;i<a2.length;i++) {
		item = a2[i]
		if (a1.includes(item)) { n++; }
	}
	return n 
}


function set_nentries() { 
	var nentries = document.getElementById('nentries');
	nentries.innerText = '# Entries ' + current_active_ids_set.length;
}

function toggle_sidebar() {
	if (sidebar_state == 'closed') {
		open_sidebar()
		sidebar_state = 'open';
		btn.innerHTML = '<span>&#215;</span>'
	} else {
		close_sidebar()
		sidebar_state = 'closed';
		btn.innerHTML = '<span>&#43;</span>'
	}
}

function open_sidebar() {
document.getElementById("mySidebar").style.width = "230px";
document.getElementById("content").style.marginLeft = "220px";
}


function close_sidebar() {
document.getElementById("mySidebar").style.width = "0px";
document.getElementById("content").style.marginLeft= "25px";
}

function make_button(name, button_type) {
	//creates a button to indicate search field or special term
	var button = document.createElement('button'); 
	button.innerHTML = name;
	button.name = name;
	button.id = name + '_button';
	button.type = 'button';
	button.classList.add('search_button')
	button.classList.add(button_type)
	button.addEventListener('click',toggle_button);
	var button_location = document.getElementById('extended_search_list')
	button_location.append(button)
}

function toggle_button(event) {
	button = event.target;
	console.log(button.innerHTML);

	if (button.innerHTML == 'AND') {
		button.innerHTML = 'OR'
		combine.value = ' '
	} else if (button.innerHTML == 'OR') {
		button.innerHTML = 'AND'
		combine.value = 'combine'
	}
	if (button.innerHTML == 'EXACT') {
		button.innerHTML = 'CONTAINS'
		exact.value = 'contains'
	} else if (button.innerHTML == 'CONTAINS') {
		button.innerHTML = 'EXACT'
		exact.value = 'exact'
	}
}

function toggle_sorting() {
	var ascending = '<i class="fas fa-sort-alpha-down"></i>'
	var descending= '<i class="fas fa-sort-alpha-up"></i>'
	console.log('sorting')
	var button = document.getElementById('sorting')
	var direction= document.getElementById('direction')
	console.log(button.innerHTML);
	if (button.innerHTML.includes(ascending)) {
		button.innerHTML = descending;
		direction.value = 'descending'
		sorting_direction = 'descending'
	} else if (button.innerHTML.includes(descending)) {
		button.innerHTML = ascending;
		direction.value = 'ascending'
		sorting_direction = 'ascending'
	}
		
}

function get_sorting_direction() {
	var ascending = '<i class="fas fa-sort-alpha-down"></i>'
	var button = document.getElementById('sorting')
	if (button.innerHTML.includes(ascending)) { return 'ascending';}
	else { return 'descending';}
}

function get_sorting_category() {
	var sort_menu= document.getElementById('sorting_option');
	return sort_menu.value;
}

function get_query() {
	var query = document.getElementById('exampleFormControlInput1');
	return query.value;
}

window.addEventListener('DOMContentLoaded', function () {
	console.log(us,us.useable)
	if (us && us.useable) {
		var filters = us.filters;
		for (let i=0;i<filters.length;i++) {
			filter = filters[i];
			console.log(filter);
			toggle_filter(filter)
		}
		console.log('filters',filters,selected_filters)
	}
})



//-----------------------------------------
function _make_nouirange(start,end) {
	// defines a range dictionary for the nouislider
	var span = end - start;
	console.log(span)
	var range = {'min':start,'max':end}
	// if the spanned time is short return a linear slider
	if (span <= 100) {return range;}
	// if the spanned time is longer return a non linear slider
	// allocating less space to earlier times
	var fp = start+30;
	if (fp < 1800) {fp = 1800}
	if (span <= 200) {
		range['15%']= fp
		return range
	}
	var sp = start+100;
	if (sp < 1900) {sp =1900}
	range['5%']= fp
	range['40%']= sp
	return range
}

// date slider
// Multi slider for Date range
var start = date_range['earliest_date'];
var end = date_range['latest_date'];
if (start === end) {start -=1; end += 1;}
var range = _make_nouirange(start,end)
console.log(range);
var multi_slider = document.getElementById('years');
var dateValues = [
		document.getElementById('event-start'),
		document.getElementById('event-end')
];
var start_range = 1700;
if (start < start_range) {start_range = start;}
noUiSlider.create(multi_slider, {
	start: [start, end],
	connect: true,
	range: range, //{'min':start_range,'15%':1800,'max':end},
	steps: 50,
	//tooltips: true,
	format: {to: function (value) {return Math.floor(value)},
		from: function (value) {return Math.floor(value)}},
});


function check_overlap(low,high){
	//compare start and end date of a figure with start end date of the year slider
	if (!low) { return false;} //figure should always have start date to be visible
	if (!high) { // if end dat is not available check whether start date is after start
		if (low >= start && low <= end) { return true;}
		return false
	}
	if (low <= start && high >= start){ return true;}
	if (low >= start && high <= end){ return true;}
	if (low <= end && high >= start){ return true;}
	return false;
}

function date_filter_installations() {
	// updates a list of installations ids that are outside the range of the date slider
	// updates the displayed installations and the counts
	/*
	for (i = 0; i< city_active_installation_ids.length; i++) {
		installation_id = city_active_installation_ids[i];
		installation = document.getElementById(installation_id)
		if (!installation) { continue;}
		var low = parseInt(installation.getAttribute('data_map_start_date'))
		var high = parseInt(installation.getAttribute('data_map_end_date'))
		var overlap = check_overlap(low,high);
		if ( overlap ) {
			if (date_exclude_installation_ids.includes(installation_id) ) { 
				var index = date_exclude_installation_ids.indexOf(installation_id);
				date_exclude_installation_ids.splice(index,1);
			}
		} else { 
			if (!date_exclude_installation_ids.includes(installation_id) ) {
				date_exclude_installation_ids.push(installation_id); 
			}	
		}
	}
	hide_show_elements();
	*/
}



multi_slider.noUiSlider.on('slide',handleYearSliderValues);
multi_slider.noUiSlider.on('set',handleYearSlider);
function handleYearSliderValues(values,handle) {
	//set start and end values based on the year slider, 
	console.log('setting values')
	start= values[0];
	end= values[1];
	dateValues[handle].innerHTML = values[handle];
}

function handleYearSlider(values,handle) {
	//set start and end values based on the year slider, 
	console.log('setting slider')
	start= values[0];
	end= values[1];
	dateValues[handle].innerHTML = values[handle];
	//code to filter instances
	if (!century_set_date_slider) {
		update_date_slider_active_ids();
	}
}

function set_year_slider(start,end) {
	console.log('set year',start,end)
	century_set_date_slider = true;
	multi_slider.noUiSlider.set([start,end])
	century_set_date_slider = false;
	update_date_slider_active_ids();
}

function reset_year_slider() {
	multi_slider.noUiSlider.reset()
}
//-----------------------
// date filtering

function update_date_slider_to_century_filter() {
	if (filter_active_dict['century'] == 'active') {
		reset_year_slider();
		return;
	}
	var fad_keys = Object.keys(filter_active_dict);
	var centuries = []
	for (let i=0;i<fad_keys.length;i++) {
		var key = fad_keys[i];
		if (filter_active_dict[key] == 'inactive') { continue;}
		if (key.includes('century')) {
			var name = key.split(',')
			if (name.length == 2) {
				name = name[1];
				centuries.push(parseInt(name.substring(0,2)))
			}
		}
	}
	var start_century = Math.min(...centuries)
	var end_century = Math.max(...centuries)
	var start_year = start_century * 100 - 100
	var end_year = end_century * 100 - 1
	console.log(centuries, start_year, end_year);
	set_year_slider(start_year,end_year)
}

function update_date_slider_active_ids() {
	date_slider_active_ids = [];
	var keys = Object.keys(id_year_range_dict);
	for (let i=0;i<keys.length;i++) {
		var key = keys[i];
		var year_range = id_year_range_dict[key];
		if (!year_range) { continue;}
		var [low,high] = year_range;
		if (check_overlap(...year_range)) {
			date_slider_active_ids.push(key)
		}
	}
	console.log('dsai',date_slider_active_ids)
	update_hide_show_instances();
	update_count_dict();
	update_sidebar();
	set_nentries();
}

//---------------------------------------------------------------------------------------