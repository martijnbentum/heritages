document.onkeydown = checkKey;

var clicked_instance = '';
var view_type = 'tile_view';

function set_clicked_instance(identifier) {
	clicked_instance = identifier;
}


function checkKey(e) {
	//handle keyboard input, escape key to exit model
	//right and down arrow keys to go forward
	//left and up arrow keys to go back
	e = e || window.event;
	var direction = ''
	if (e.keyCode == 27) {
		modal.style.display = "none";
		in_modal_state = false;
	} else if (e.keyCode == 37 || e.keyCode == 38) {
		next_prev_picture('back')
	} else if (e.keyCode == 39 || e.keyCode == 40) {
		next_prev_picture('forward')
	}
}

function next_prev_picture(direction) {
	if (!in_modal_state) {return}
	i = find_identifier_index(current_identifier);
	console.log('next_prev_picture',i,current_identifier);
	if (direction == 'back' || direction == 'prev') {
		if (i == 0) {i = active_ids.length -1;}
		else { i -= 1;}
	}
	if (direction == 'forward' || direction == 'next') {
		if (i == active_ids.length -1) { i = 0; }
		else { i += 1;}
	}
	display_large_image(active_ids[i]);
}


var tiles= document.getElementsByClassName('tile')
for ( i =0; i < tiles.length; i++ ){
	tile= tiles[i];
	//console.log(tile);
}

function find_identifier_index(identifier) {
	for ( i =0; i < active_ids.length; i++ ){
		active_id= active_ids[i];
		//console.log(tile,'tile');
		if (active_id == identifier) {return i;}
	}
}
	
// whether the large image is shown in the modal
var in_modal_state = false;
// identifier of the instance of which the image is shown
var current_identifier= '';
// Get the modal
var modal = document.getElementById("myModal");
//elements that display the image, title and date
var modal_title = document.getElementById("modal-title");
var modal_icon= document.getElementById("modal-icon");
var modal_img= document.getElementById("modal-img");
var modal_date= document.getElementById("modal-date");
var modal_edit= document.getElementById("modal-edit-link");
// Get the <span> element that closes the modal, OBSOLETE??
var span = document.getElementsByClassName("close")[0];
var close_modal= document.getElementById("close_modal");
var prev_modal= document.getElementById("prev_modal");
var next_modal= document.getElementById("next_modal");
var image_reel_on = false;
var one_of_x = document.getElementById('one_of_x');

function _handle_image_urls(d) {
	// d contains field image_urls, a sting of comma seperated image urls
	// creates an array with image urls and excludes the thumbnail url from the list
	var image_urls = d.image_urls.split(',')
	if ( image_urls.length == 1 && typeof(image_urls[0]) == 'string') {return []}
	var thumbnail = d.thumbnail
	var index = image_urls.indexOf(thumbnail)
	if ( index == -1 ) { return image_urls }
	image_urls.splice(index,1)
	return image_urls
}

function _get_image_url(image_urls) {
	if (image_urls.length == 0) {
		var image_url = '';
	} else if (image_urls.length > 0) {
		var image_url = '/media/' +image_urls[0];
	} else { 
		var image_url = '/media/' + d['thumbnail'];
	}
	return image_url
}

async function get_instance_info(identifier,fields= false) {
	//gets information of an instance, instance is loaded based on 
	//the identifier field
	//fields 	the field names the info should be gathered from
	//		false or 'all' returns the dict of the instance (not property values)
	//returns a dictionary of field name field info or a json representation 
	//		of the instance
	var url = '/utilities/ajax_instance_info/' + identifier 
	if (fields) { url += '/' + fields ;}
	const response = await fetch(url); 
	const instance_info = await response.json();
	return instance_info;
}


async function display_large_image(identifier) {
	//displays large image of a given instance (identified with identifier)
	image_reel_on = false;
	one_of_x.innerText= '';
	fields = 'thumbnail,edit_url,title,pk,date,icon,image_urls,detail_url'
	var d  = await get_instance_info(identifier,fields)
	console.log(d)
	in_modal_state = true;
	current_identifier = identifier;
	modal_title.innerText = d['title'];
	modal_icon.className=d['icon'] + ' fa-2x modal-icon';
	modal_date.innerText = d['date'];
	var image_urls = _handle_image_urls(d);
	var image_url = _get_image_url(image_urls)
	modal_img.src = image_url
	modal_edit.href = "/" +d['detail_url'].replace(':','/') + "/" + d['pk'] 
	modal.style.display = "block";
	if (image_urls.length > 1) {
			one_of_x.innerText= 1 + '/' + image_urls.length;
			setTimeout(switch_images,2100,image_urls,image_urls[0],identifier)
			image_reel_on = true;
	}
}


function switch_images(image_urls,current_image, identifier) {
	console.log(image_urls,current_image,image_reel_on);
	var next_modal= document.getElementById("");
	var index = 0;
	if (in_modal_state && image_reel_on 
		&& current_identifier == identifier) {
		for ( i =0; i < image_urls.length; i++ ){
			url= image_urls[i];
			if (url  == current_image) {
				console.log(url,i,image_urls.length);
				if (i == (image_urls.length -1)) {index = 0;}
				else {index = i + 1;}
				console.log(index)
				modal_img.src = '/media/' +image_urls[index]
			}
		}
		console.log(image_urls,image_urls[index],index);
		one_of_x.innerText= (index +1) + '/' + image_urls.length;
		
		setTimeout(switch_images,3000,image_urls,image_urls[index],identifier);
	}
}


close_modal.onclick = function() {
	modal.style.display = "none";
	in_modal_state = false;
}

prev_modal.onclick = function() {
	next_prev_picture('prev');
}
next_modal.onclick = function() {
	console.log('hello');
	next_prev_picture('next');
}

