import re

# tilefilms can be embedded but not supported, 
# 	because link does not give id of video
# openbeelden can be embedded but not supported,
# 	because uses different embed element
# schooltv can be embedded but not supported,
# 	because link does not give id of video
not_supported_sources = 'tilefilms,npostart,bpb,britishpathe,haagsgemeentearchief'
not_supported_sources += ',beeldbankwo2,openbeelden,schooltv,imbd,itunes,idfa'
not_supported_sources += ',amazon,sonyclassics,npo'
not_supported_sources = not_supported_sources.split(',')

def handle_youtube(source):
	print(source,9)
	output = 'https://www.youtube.com/embed/'
	o = re.search('v=\S*',source)
	if o and o.group():
		o =output + o.group().split('v=')[-1]
		print('embed source link (youtube):',o)
		return o
	elif 'embed' not in source: 	
		v= source.split('/')
		print(v)
		o = 'https://www.youtube.com/embed/' + v[-1]
		print('embed source link (youtube):',o)
		return o
	elif output in source: return source
	else: 
		print('could not convert youtube link to embed format:',source)
		return ''


def handle_vpro(source):
	output = 'https://embed.vpro.nl/player/?id='
	o = re.search('WO_VPRO_\d*', source)
	if o.group():
		output += o.group() + '&profile=vpro'
		print('embed source link vpro:',output)
		return output
	print('failed to convert vpro link to embed format:',source)


f = {'youtube':handle_youtube,'vpro':handle_vpro}
supported_sources = list(f.keys())


def _check_not_supported(source):
	for s in not_supported_sources:
		if s in source: print('source is not supported:',s,'\n',source)
	print('source is unknown:',source)


def _check_source_is_supported(source):
	source = source.replace('.','')
	for s in supported_sources:
		if s in source: 
			print('source is supported:',s,source)
			return s
	return ''


def link2embed_source(instance, primary='', secondary='', tirtiary= ''):
	'''maps link to embed code
	primary - tirtiary 		links in descending order of importance
	returns embed code for the first link that can be mapped to embed code
	'''
	source_type = ''
	for link in [primary, secondary, tirtiary]:
		print('handling link:',link)
		if not link: 
			print('link field',link,'is empty')
			continue
		source_type = _check_source_is_supported(link)
		if not source_type:
			_check_source_is_supported(link)
			continue
		return f[source_type](link)
	return ''


	
	
