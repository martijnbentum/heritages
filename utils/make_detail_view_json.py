from django.urls import reverse
import json
from sources import models as sources_models
from utils import search_view_helper as svh
from utils import model_util as mu
from utils import view_util as vu
from pathlib import Path

exclude_names = ['location', 'language'] + sources_models.names
exclude_names = [x.lower() for x in exclude_names]

def detail_args(instance):
    model_name = instance._meta.model_name
    if model_name == 'person': import persons.views as views
    elif model_name == 'famine': import misc.views as views
    else: import sources.views as views
    function = getattr(views, f'detail_{model_name}_view')
    request = svh.make_dummy_request_for_user_search()
    args = function(request, instance.pk, only_return_args = True)
    return args

def secondary_instance_to_json(instance):
    d = {}
    if type(instance) == str:
        d['name'] = instance
        d['identifier'] = None
        d['model_name'] = None
        d['url'] = None
        return d
    model_name = instance._meta.model_name
    print(f'{model_name} {instance.pk} {instance}')
    d['name'] = str(instance)
    if model_name.lower() in exclude_names: 
        d['identifier'] = None
        d['url'] = None
    else:    
        d['identifier'] = instance.identifier
        d['url'] = get_url(instance)
    d['model_name'] = model_name
    return d

def contributer_list(instance):
    c = vu.Crud(instance)
    cl = c.contributer_list
    return [x for x in cl if x != '' and x != 'mb']
    

def get_image_filenames(instance, image_dir):
    urls = mu.instance2image_urls(instance)
    if type(urls) == str: urls = [urls]
    fn = [Path(x).name for x in urls]
    if fn == ['']: fn = []
    o = []
    for f in fn:
        path = Path(f'{image_dir}images/{f}')
        if not path.exists(): 
            print(f'File not found: {path}')
            continue
        print('adding file:', path)
        o.append(str(path).replace(image_dir, ''))
    return o

def get_url(instance, base_url = 'hunger.rich.ru.nl'):
    if instance._meta.model_name in exclude_names: return ''
    url = reverse(instance.detail_url, kwargs = {'pk': instance.pk})
    return f'{base_url}{url}'
    

def instance_to_json(instance, 
    image_dir = 'rdr_hoh/'):
    d = secondary_instance_to_json(instance)
    fields = ['title_original', 'title_english', 'date_field', 'description']
    fields += ['source_link', f'{instance._meta.model_name}_type']
    for field in fields:
        if hasattr(instance, field): 
            value = getattr(instance, field)
            if 'type' in field: field = 'type'
            if field in ['date_field', 'type']: 
                value = str(value)
            d[field] = value
        else: 
            if 'type' in field: field = 'type'
            d[field] = None
    image_filenames = get_image_filenames(instance, image_dir)
    d['image_filenames'] = image_filenames
    d['keywords'] = instance.keyword_names.split(', ')
    if instance._meta.model_name == 'person':
        d['viaf'] = instance.viaf
        d['pseudonyms'] = instance.pseudonyms
    d['meta_data_contributer_list'] = contributer_list(instance)
    return d

def args_to_json(args, instance = None):
    if not instance: instance = args['instance']
    d = {'instance': instance_to_json(instance), 'connections': {}}
    for key, value in args.items():
        if key in ['us','instance','page_name']: continue
        f = secondary_instance_to_json
        d['connections'][key] = [f(instance) for instance in value]
    return d

def make_all_detail_views(save = False, 
    output_dir = 'rdr_hoh/', name = 'main_data.json'):
    instances = mu.get_all_instances(flag_filter_person = False,
        add_famine = True)
    output = {}
    for x in instances:
        model_name = x._meta.model_name
        print(f'Processing {model_name} {x.pk} {x}')
        if model_name not in output.keys(): output[model_name] = []
        args = detail_args(x)
        d = args_to_json(args, x)
        output[model_name].append(d)
    if save:
        filename = f'{output_dir}{name}'
        print(f'Saving to {filename}')
        with open(filename, 'w') as f:
            json.dump(output, f, indent = 4)
    return output
        

