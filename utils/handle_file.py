from striprtf.striprtf import rtf_to_text


def handle_pdf(file_field):
	return {'file_type':'pdf','file':file_field.url}

def handle_image(file_field):
	return {'file_type':'image','file':file_field.url}

def handle_txt(file_field):
	text = _open_text(file_field.url)
	return {'file_type':'text','file':text}

def handle_rtf(file_field):
	text = _open_text(file_field.url)
	text = rtf_to_text(text)
	return {'file_type':'text','file':text}

filetype2function = {'pdf':handle_pdf,'jpg':handle_image,'jpeg':handle_image}
filetype2function.update({'png':handle_image,'tiff':handle_image})
filetype2function.update({'bmp':handle_image,'eps':handle_image})
filetype2function.update({'txt':handle_txt,'rtf':handle_rtf,'rtfd':handle_rtf})

def _open_text(url):
	return open(url[1:]).read()

def _check_file(file_field):
	if not file_field: return ''
	file_type = file_field.name.split('.')[-1].lower()
	if file_type not in filetype2function.keys():
		print(file_type,'not supported file type',filetype2function.keys())
		return ''
	return file_type

def handle_file(instance,file_field):
	file_type = _check_file(file_field)
	print('handling file:',file_field)
	if not file_type: return {}
	return filetype2function[file_type](file_field)

	
		
	
