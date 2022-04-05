var clicked_instance = '';
var view_type = 'row_view';

function set_clicked_instance(identifier) {
	clicked_instance = identifier;
}

function toggle_row_view(identifier) {
	//toggles the expanded row view by calling get_instance_info
	var [app, model, pk] = identifier.split("_")
	get_instance_info(identifier)
}
		
async function get_instance_info(identifier) {
	// loads instance information from the server and
	// toggles the row view between short and expanded
	var path = '/utilities/ajax_instance_info/' + identifier
	path += '/setting_names,description,famine_names'
	const response = await fetch(path);
	const data = await response.json();
	var description = document.getElementById(identifier + '_description')
	if ( description.innerText.length <= 180 ) {
		var html= data.description;
		if (data.setting_names) {
			html += "<br>"
			html += '<span class="blue"> Location: ' +data.setting_names + '</span>'
		}
		if (data.famine_names) {
			html += "<br>"
			html += '<span class="famine-color"> Famine: ' 
			html += data.famine_names + '</span>'
		}
		description.innerHTML= html;
	} else {
		description.innerHTML= data.description.substring(0,177) +'...'
	}
}

