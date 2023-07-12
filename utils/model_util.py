from django.apps import apps
from django.db import models
from django.db.models.fields.files import ImageFileDescriptor
from django.db.models.fields.files import ImageField, FileField
import random
import string
import itertools
from utils.general import sort_count_dict, make_century_dict, sort_dict_on_keys

n = 'Image,PictureStory,Infographic,Film,Music,Text,Videogame'
n += ',Recordedspeech,Memorialsite,Artefact,Person'
all_model_names = n.split(',')


class info():
    '''inherit from this class to add extra viewing functionality for models'''

    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def view(self):
        '''show all attributes of instance'''
        print(self.UNDERLINE,self.__class__,self.END)
        n = max([len(k) for k in self.__dict__.keys()]) + 3
        for k in self.__dict__.keys():
            print(k.ljust(n),self.BLUE,self.__dict__[k], self.END)

    @property
    def info(self):
        n = max([len(k) for k in self.__dict__.keys()]) + 3
        m = '<table class="table table-borderless" >'
        for k in self.__dict__.keys():
            if k == '_state' or k == 'id': continue
            m += '<tr class="d-flex">'
            m += '<th class="col-2">'+k.ljust(n)+'</th>'
            m += '<td class="col-8">'+str(self.__dict__[k]) +'</td>'
        m += '</table>'
        return m

    


def id_generator(id_type= 'letters', length = 9):
    '''probably obsolete, generate a random identifier string for an 
    instance.'''
    if id_type == 'letters':
        return ''.join(random.sample(string.ascii_letters*length,length))
    if id_type == 'numbers':
        return int(''.join(random.sample('123456789'*length,length)))


def compare_model_dicts(sd,od):
    '''Compare model class dictionary to compare the similarity of two model 
    instances. 
    helper function of compare_instances
    '''
    equal,similar = True, True
    ntotal,nsame,nsimilar = len(sd.keys())-2, 0, 0
    for k in sd.keys():
        # skip fields that are different by definition
        if k in ['id','_state']:continue 
        if sd[k] == od[k]: 
            nsame +=1
            nsimilar +=1
        elif sd[k] in ['',None] or od[k] in ['',None]: 
            equal = False
            nsimilar +=1
        else: 
            equal,similar = False,False
    perc_same,perc_similar = nsame/ntotal,nsimilar/ntotal
    return equal,perc_same,similar,perc_similar

def compare_instances(self,other):
    '''Compare two instances.
    If each field for the two instances are identical returns equal true

    If fields for the instances only differs  whereby one has default empty 
    value (i.e. none or '')
    return similar true

    Also returns percentage for both equal and similar
    '''
    if type(self) != type(other):
        # print(self,'is not of the same type as:',other,type(self),type(other))
        return False,0,False,0
    sd, od = self.__dict__, other.__dict__
    return compare_model_dicts(sd,od)

def compare_queryset(qs):
    '''Compare all unordered paired combinations of instances in a queryset a
    determines the equality / similarity of the pair. (see compare_ instances)
    '''
    equal_list,similar_list,complete_list = [],[],[]
    #create all unordered paired combinations in the qs
    for a,b in itertools.combinations(qs,2): 
        equal,pe,similar,ps = compare_instances(a,b)
        line = [a,b,equal,pe,similar,ps]
        if equal: equal_list.append(line)
        if similar: similar_list.append(line)
        complete_list.append(line)
    return equal_list, similar_list, complete_list
        

def instance2names(instance):
    # s = str(type(instance)).split("'")[-2]
    # app_name,_,model_name = s.split('.')
    app_name= instance._meta.app_label
    model_name = instance._meta.model_name.capitalize()
    if model_name == 'Picturestory': model_name = 'PictureStory'
    return app_name, model_name

def instance2name(instance):
    app_name, model_name = instance2names(instance)
    return model_name
    
        
def copy_complete(instance, commit = True):
    '''copy a model instance completely with all relations.'''
    copy = simple_copy(instance, commit)
    app_name, model_name = instance2names(instance)
    for f in copy._meta.get_fields():
        if f.one_to_many:
            for r in list(getattr(instance,f.name+'_set').all()):
                rcopy = simple_copy(r,False,False)
                setattr(rcopy,model_name.lower(), copy)
                rcopy.save()
        if f.many_to_many:
            getattr(copy,f.name).set(getattr(instance,f.name).all())
    return copy


def simple_copy(instance, commit = True,add_copy_suffix = True):
    '''Copy a model instance and save it to the database.
    m2m and relations are not saved.
    '''
    app_name, model_name = instance2names(instance)
    model = apps.get_model(app_name,model_name)
    copy = model.objects.get(pk=instance.pk)
    copy.pk = None
    print('copying...')
    for name in 'title,name,caption,first_name'.split(','):
        if hasattr(copy,name):
            print('setting',name)
            copy.view()
            setattr(copy,name,getattr(copy,name)+ ' !copy!')
            copy.view()
            break
    if commit:
        copy.save()
    return copy


def model_text_field_names(model, include_char_fields = True,
    exclude_fields = True):
    if exclude_fields == True: 
        exclude_names = 'link,field,loc_ids,comments,filename'.split(',')
    else: exclude_names= []
    output = []
    for field in model._meta.fields:
        name = field.name
        if len([exclude for exclude in exclude_names if exclude in name])>0:
            continue
        if isinstance(field,models.CharField) and include_char_fields:
            output.append(field.name)
        if isinstance(field,models.TextField):
            output.append(field.name)
    return output

def make_text_field_name_dict(include_char_fields = True, 
    exclude_fields = True):
    models = get_all_models()
    d = {}
    for model in models:
        field_names = model_text_field_names(model,include_char_fields,
            exclude_fields)
        d[model._meta.model_name] = field_names
    return d

def instance_to_text(instance):
    field_names = model_text_field_names(instance._meta.model)
    output = []
    for name in field_names:
        text = getattr(instance,name)
        if text:output.append(text)
    return ' '.join(output)
    
def all_instances_to_text():
    instances = get_all_instances()
    output = []
    for instance in instances:
        text = instance_to_text(instance)
        if text:output.append(text)
    return ' '.join(output)
        
        
            
        
        


def model_image_field_names(model, only_image_fields = False):
    fields = model._meta.get_fields()
    file_field_names = []
    for field in fields:
        if field.get_internal_type() == 'FileField':
            if only_image_fields and type(field) != ImageField: continue
            file_field_names.append(field.name)
            temp = field
    return file_field_names

        
def make_models_image_file_dict(only_image_fields=False):
    '''
    creates a dictionary with all models containing a image or file field.
    dict contents:
    key         app_name, model name (tuple)
    value       list of field_names (can either be image or file field
    '''
    from .export import get_all_models, get_selected_models
    all_models = get_all_models()
    selected_models = get_selected_models()
    d = {}
    for model in selected_models:
        file_field_names = model_image_field_names(model, only_image_fields)
        if file_field_names: 
            app_name, model_name = instance2names(model)
            d[app_name, model_name] = file_field_names
    return d

def get_all_models(model_names=[]):
    if not model_names: model_names = all_model_names
    model_names.sort()
    model_names = [n.lower() for n in model_names]
    all_models = apps.get_models()
    models = []
    for model_name in model_names:
        for model in all_models:
            if model._meta.model_name == model_name: models.append(model)
    return models

def get_all_instances(model_names = [],flag_filter_person = True, 
    exclude_persons = False):
    models = get_all_models(model_names=model_names)
    instances = []
    for x in models:
        if x._meta.model_name == 'person': 
            if exclude_persons: continue
            if flag_filter_person: 
                instances.extend(x.objects.filter(flag = True))
        else:instances.extend(x.objects.all())
    return instances

def get_all_flagged_instances(exclude_persons = True):
    if exclude_persons:
        n = 'Image,PictureStory,Infographic,Film,Music,Text,Videogame'
        n += ',Recordedspeech,Memorialsite,Artefact'
        model_names = n.split(',')
    else: model_names = ''
    models = get_all_models(model_names=model_names)
    instances = []
    for x in models:
        i = x.objects.filter(flag = True)
        if i.count() > 0:
            instances.extend(i)
    return instances
        

def instance2image_urls(instance):
    '''returns all urls of an instance to all attached images 
    (i.e. ImageFields).'''
    o = []
    for field in instance._meta.fields:
        if type(field) == ImageField:
            x= getattr(instance,field.name)
            if x.name:
                o.append(x.url)
    return ','.join(o)

def instance2file_urls(instance):
    '''returns all urls of an instance to all attached images 
    (i.e. ImageFields).'''
    o = []
    for field in instance._meta.fields:
        if type(field) == FileField:
            x= getattr(instance,field.name)
            if x.name:
                o.append(x.url)
    return ','.join(o)

def instance_has_attached_files(instance):
	if instance2image_urls(instance): return True
	if instance2file_urls(instance): return True
	return False
	

def get_all_image_urls(flagged = True, exclude_persons = True, 
    exclude_thumbnails = True, only_with_permission = False,
    only_images_and_monuments = False, not_explicit = False):
    if flagged: instances = get_all_flagged_instances(exclude_persons)
    else: instances = get_all_instances(exclude_persons = exclude_persons)
    output = []
    for instance in instances:
        if only_with_permission and not instance.has_permission: 
            continue
        if not_explicit and instance.is_explicit:continue
        if only_images_and_monuments:
            if instance._meta.model_name not in ['memorialsite','image']:
                continue
        urls = instance2image_urls(instance)
        for url in urls.split(','):
            if not url: continue
            if 'thumbnail' in url: continue
            else: output.append(url)
    return output
        
def get_random_image_urls(n = 1, flagged = True, exclude_persons = True,
    exclude_thumbnails = True, only_with_permission=True, 
    only_images_and_monuments = True, not_explicit = True):
    urls = get_all_image_urls(flagged, exclude_persons, exclude_thumbnails,
        only_with_permission, only_images_and_monuments, not_explicit)
    if len(urls) < n: return urls
    return random.sample(urls,n)

def instances2country_counts(instances):
    '''names and counts of countries that are linked to a list of instance.'''
    count_d = {}
    instances_d = {}
    for instance in instances:
        if instance.country_field:
            countries = instance.country_field.split(',')
            _add_to_count_instance_dict(count_d,instances_d,countries,instance)
    count_d = sort_count_dict(count_d)
    return count_d, instances_d

def instances2keyword_category_counts(instances):
    '''names and counts of category keywords that are linked to a list of 
    instance.'''
    count_d = {}
    instances_d = {}
    for instance in instances:
        if instance.keyword_category_field:
            keywords = instance.keyword_category_field.split(',')
            _add_to_count_instance_dict(count_d,instances_d,keywords,instance)
    count_d = sort_count_dict(count_d)
    return count_d, instances_d

def instances2model_counts(instances):
    '''names and counts of models that are linked to a list of instance.'''
    count_d = {}
    instances_d = {}
    map_names = {'Recordedspeech':'Recorded speech',
        'Memorialsite':'Memorial site'}
    map_names.update({'PictureStory':'Picture story'})
    for instance in instances:
        name = instance2name(instance)
        if name in map_names.keys(): name = map_names[name]
        _add_to_count_instance_dict(count_d,instances_d,[name],instance)
    count_d = sort_count_dict(count_d)
    return count_d, instances_d

def instances2rating_counts(instances):
    '''names and counts of ratings that are linked to a list of instance.'''
    count_d = {}
    instances_d = {}
    for instance in instances:
        if not hasattr(instance,'rated'): name = 'general'
        elif not instance.rated: name = 'general'
        else: name = instance.rated.name
        _add_to_count_instance_dict(count_d,instances_d,[name],instance)
    count_d = sort_count_dict(count_d)
    return count_d, instances_d

def instances2century_counts(instances):
    count_d = {}
    instances_d = {}
    century_dict = make_century_dict()
    for instance in instances:
        if not instance.date_field: continue
        name = century_dict[int(instance.date_field.year/100)]
        _add_to_count_instance_dict(count_d,instances_d,[name],instance)
    count_d = sort_dict_on_keys(count_d)
    return count_d, instances_d

def instances2famine_counts(instances):
    count_d = {}
    instances_d = {}
    for instance in instances:
        if instance.famine_field:
            famines = instance.famine_field.split(',')
            _add_to_count_instance_dict(count_d,instances_d,famines,instance)
    count_d = sort_count_dict(count_d)
    return count_d, instances_d
    
def _add_to_count_instance_dict(count_d,instances_d,names, instance):
    for name in names:
        if name not in count_d.keys(): count_d[name] ,instances_d[name] = 0, []
        count_d[name] +=1
        instances_d[name].append(instance)

def instance2keyword_categories(instance):
    '''return all category keywords linked to a given instance in csv format.'''
    kws = instance.keywords.all()
    o = []
    for kw in kws:
        name = kw.category
        if not name: continue
        if name not in o:o.append(name)
    return ','.join(o)
        
def instance2keyword_detail(instance):
    '''return all non category keywords linked to a given instance in 
    csv format.'''
    kws = instance.keywords.all()
    o = []
    for kw in kws:
        if kw.category_keyword: continue
        if kw.name not in o:o.append(kw.name)
    return ','.join(o)

def instance2famines(instance):
    famines = instance.famines.all()
    o =[]
    for famine in famines:
        names = famine.names.all()
        if names: 
            name = names[0].name
            if name not in o: o.append(name)
    return ','.join(o)
    
def identifier2instance(identifier):
    app_name, model_name, pk = identifier.split('_')
    model = apps.get_model(app_name,model_name)
    return model.objects.get(pk=pk)

def update_all_instances(remove_cruds = False):
    '''saves all instances to update stored values on each instance.
    e.g. keyword names are stored on a text instance, if keywords are changed
    the info on the text instance is only changed when it is saved.
    load all instances and save them
    remove_cruds        remove the crud events generated by easy audit
                        for each edit to a model, saving instances will
                        generate cruds without any information which
                        fill up the database
    ''' 
    instances = get_all_instances(flag_filter_person=False)
    for instance in instances:
        instance.save()
    if remove_cruds:
        from utilities.management.commands import clean_db
        clean_db.remove_crud_events_without_changes()

def instance_has_thumbnail(instance):
    return bool(instance.thumbnail)

def instance_has_image_file(instance):
    image_field_names = model_image_field_names(instance)
    image_field_names.pop(image_field_names.index('thumbnail'))
    values = []
    for name in image_field_names:
        values.append(bool(getattr(instance,name)))
    return bool(sum(values))

def check_license_and_reference_field(instance, 
    check_type = 'reference & license'):
    field_names = 'license_image,license_thumbnail,reference'.split(',')
    if check_type == 'reference': field_names = ['reference']
    elif check_type == 'license': 
        field_names.pop(field_names.index('reference'))
    values = []
    for name in field_names:
        if not hasattr(instance,name): continue
        if name=='license_thumbnail' and not instance_has_thumbnail(instance): 
            continue
        if name == 'license_image' and not instance_has_image_file(instance):
            continue
        values.append(bool(getattr(instance,name)))
    if len(values) == 0: return 'complete'
    if sum(values) == 0: return 'empty'
    if len(values) == sum(values): return 'complete'
    return 'partial'
        
def get_instances_without_license_or_reference(
    check_type = 'reference & license', model = 'all', add_info_form = None):
    if add_info_form:
        check_type = add_info_form['check_empty']
        model = add_info_form['model'].lower()
    if model == 'all': instances = get_all_instances()
    else: instances = get_all_instances(model_names = [model])
    output = []
    for instance in instances:
        status = check_license_and_reference_field(instance, check_type)
        if status == 'complete': continue
        output.append(instance)
    return output
        
        
    
