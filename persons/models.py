from django.db import models
from utilities.models import SimpleModel
from utils.model_util import info, instance2keyword_categories, instance2keyword_detail
from utils.model_util import instance2famines
from utils.instance2countries import instance2countries
from misc.models import Keyword, Famine,License
from locations.models import Location
from utils.map_util import instance2related_locations, field2locations
from utilities.models import instance2name, instance2color, instance2map_buttons
from partial_date import PartialDateField


def make_simple_model(name):
    exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

names = 'Gender,Nationality,Occupation,Affiliation'
names = names.split(',')

for name in names:
    make_simple_model(name)

class Person(models.Model, info):
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    name = models.CharField(max_length=1000,default='')
    pseudonyms = models.CharField(max_length=1000,default='')
    pseudonym_precedent= models.BooleanField(default = False)
    gender= models.ForeignKey(Gender,**dargs)
    nationality = models.ForeignKey(Nationality,**dargs)
    date_of_birth= PartialDateField(null=True,blank=True)
    date_of_death= PartialDateField(null=True,blank=True)
    location_of_birth = models.ForeignKey(Location, **dargs, 
        related_name='person_location_of_birth')
    location_of_death = models.ForeignKey(Location, **dargs, 
        related_name='person_location_of_death')
    occupation = models.ManyToManyField(Occupation, blank=True)
    affiliation = models.ForeignKey(Affiliation, **dargs)
    biography_link = models.CharField(max_length=3000,default='')
    comments = models.TextField(default='')
    description= models.TextField(default='')
    keywords= models.ManyToManyField(Keyword,blank=True)
    location_field = 'location_of_birth'
    flag = models.BooleanField(default = False)
    thumbnail = models.ImageField(upload_to='thumbnail/',blank=True,null=True)
    viaf = models.CharField(max_length=1000,default='')
    famines = models.ManyToManyField(Famine, blank=True)
    country_field = models.CharField(max_length=1000,default='')
    keyword_category_field = models.CharField(max_length=1000,default='')
    keyword_detail_field = models.CharField(max_length=1000,default='')
    date_field = PartialDateField(null=True,blank=True)
    famine_field = models.CharField(max_length=1000,default='')
    loc_ids= models.CharField(max_length=1000,default='')
    license_imag =models.ForeignKey(License, related_name='license_image',
        **dargs)
    license_thumbnail=models.ForeignKey(License,related_name='license_thumbnail',
        **dargs)
    reference= models.TextField(default='')

    def __str__(self):
        return self.title

    def save(self,*args,**kwargs):
        super(Person,self).save(*args,**kwargs)
        old_keyword_category_field = self.keyword_category_field
        self.keyword_category_field = instance2keyword_categories(self)
        old_keyword_detail_field = self.keyword_detail_field
        self.keyword_detail_field = instance2keyword_detail(self)
        old_country_field = self.country_field
        self.country_field = instance2countries(self)
        old_famine_field = self.famine_field
        self.famine_field = instance2famines(self)
        old_date= self.date_field
        self.date_field = self._make_date_field()
        old_loc_ids = self.loc_ids
        self._set_gps()
        new_loc_ids = old_loc_ids != self.loc_ids
        new_country =old_country_field!= self.country_field 
        new_date = old_date != self.date_field
        new_keyword_c = old_keyword_category_field != self.keyword_category_field
        new_keyword_d = old_keyword_detail_field != self.keyword_detail_field
        new_famine = old_famine_field != self.famine_field
        new = [new_loc_ids,new_country,new_date,new_keyword_c]
        new += [new_keyword_d,new_famine]
        if sum(new) > 0:
            super(Person,self).save(*args,**kwargs)

    def _set_gps(self):
        self.loc_ids = ''
        ids = []
        if self.location_of_birth: ids.append(self.location_of_birth.pk)
        if self.location_of_death: 
            pk = self.location_of_death.pk
            if pk not in ids:
                ids.append(pk)
        if ids: self.loc_ids = ','.join(map(str,ids))

    @property
    def is_explicit(self):
        return False

    @property
    def has_permission(self):
        return True

    @property
    def icon(self):
        return 'fas fa-user'

    @property
    def icon_svg(self):
        return '/media/icons/user-solid.svg'

    @property
    def title(self): #helper property to display name in overviews
        if self.pseudonym_precedent and self.pseudonyms: return self.pseudonyms
        if not self.name and self.pseudonyms: return self.pseudonyms
        return self.name

    @property
    def keyword_names(self):
        keywords= self.keywords.all().order_by('name') 
        if keywords: return ', '.join([k.name for k in keywords])
        else: return ''

    @property
    def occupations_str(self):
        return ', '.join([o.name for o in self.occupation.all()])

    @property
    def latlng(self):
        if self.location_field:
            locations = field2locations(self,self.location_field)
            if locations:return [location.gps for location in locations]
        return None

    @property
    def pop_up(self):
        if self.gender and self.gender.name == 'female':
            m = '<i class="fa fa-female fa-lg" aria-hidden="true"></i>'
        else:
            m = '<i class="fa fa-male fa-lg" aria-hidden="true"></i>'
        m += '<p class="h6 mb-0" style="color:'+instance2color(self)
        m += ';">'+self.name+'</p>'
        m += '<hr class="mt-1 mb-0" style="border:1px solid '
        m += instance2color(self)+';">'
        if self.occupation:
            m += '<p class="mt-2 mb-0">'+self.occupations_str+'</p>'
        m += instance2map_buttons(self)
        return m

    class Meta:
        unique_together = [['name','date_of_birth']]

    @property
    def edit_url(self):
        return self._meta.app_label + ':edit_' + self._meta.model_name 

    @property
    def detail_url(self):
        return self._meta.app_label+':detail_'+self._meta.model_name+'_view' 
    
    @property
    def identifier(self):
        return self._meta.app_label+'_'+self._meta.model_name+'_'+str( self.pk )

    @property
    def age(self):
        try: 
            m=self.date_of_death.start_dt.year-self.date_of_birth.start_dt.year
            return m
        except:return ''

    @property
    def date(self):
        m = ''
        if self.date_of_birth:m += str(self.date_of_birth.year)
        if self.date_of_death:m += ' - ' + str(self.date_of_death.year)
        age = str(self.age)
        if age: m += ' (' + age + ')'
        return m

    @property
    def year(self):
        if self.date_of_birth: return self.date_of_birth.year
        if self.date_of_death: return self.date_of_death.year
        return ''

    @property
    def year_range(self):
        if hasattr(self,'_year_range'): return self._year_range
        lower,higher = None,None
        if self.date_of_birth: lower = self.date_of_birth.year
        if self.date_of_death: higher = self.date_of_death.year

        if lower and higher: yr = [lower,higher]
        elif lower: yr = [lower,lower]
        elif higher: yr = [higher,higher]
        else: yr=None
        self._year_range = yr
        return self._year_range
    
        

    def _make_date_field(self):
        if self.date_of_birth: return self.date_of_birth
        return self.date_of_death
    
    @property
    def famine_names(self):
        famines= self.famines.all() 
        if famines: return ', '.join([f.names_str for f in famines])
        else: return ''

    @property
    def occupations(self):
        if hasattr(self,'_occupations'): return self._occupations
        self._occupations = list(self.occupation.all())
        return self._occupations

    @property
    def linked_instances_dict(self):
        creator= 'image_creators_set,infographic_creators_set,memorialsite_creators_set'
        creator += ',recordedspeech_creators_set,film_creators_set,artefact_creators_set'
        artist = 'picture_story_artist_set,memorialsite_artists_set'
        author = 'text_author_set,picture_story_author_set,film_writers_set'
        translator = 'text_translator_set,picture_story_translator_set'
        editor = 'text_editor_set'
        commisioner = 'memorialsite_person_commissioning_set'
        donor = 'memorialsite_person_donors_set'
        director = 'film_directors_set'
        composer = 'music_composer_set'
        field_name_sets = [creator,artist,author,translator,editor,commisioner,
            donor,director,composer]
        names = 'creator,artist,author,translator,editor,commisioner,donor,director,composer'
        names = names.split(',')
        d = {}
        for name, field_name_set in zip(names,field_name_sets):
            for field_name in field_name_set.split(','):
                field = getattr(self,field_name)
                for instance in field.all():
                    if name not in d.keys(): d[name] = []
                    if instance not in d[name]: d[name].append(instance)
        return d
            
        

        

        
        
