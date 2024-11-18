from sources import views
from utils import search_view_helper as svh

def detail_args(instance):
    model_name = instance._meta.model_name
    function = getattr(views, f'detail_{model_name}_view')
    request = svh.make_dummy_request_for_user_search()
    args = function(request, instance.pk, only_return_args = True)
    return args

def secondary_instance_to_json(instance):
    d = {}
    d['name'] = str(instance)
    d['pk'] = instance.pk
    d['model_name'] = instance._meta.model_name
    return d

def instance_to_json(instance):
    d = secondary_instance_to_json(instance)
    fields = ['title_original', 'title_english', 'date_field', 'description']
    fields += ['thumbnail','image_filename','source_link']
    for field in fields:
        d[field] = getattr(instance, field)
        if field in ['date_field','thumbnail']: d[field] = str(d[field])
    return d

def args_to_json(args):
    d = {'instance': instance_to_json(args['instance']), 'connections': {}}
    for key, value in args.items():
        if key in ['us','instance','page_name']: continue
        f = secondary_instance_to_json
        d['connections'][key] = [f(instance) for instance in value]
    return d
