from django.db import models
from django.db.models.fields.files import ImageField
from persons.models import Person
from utilities.models import SimpleModel
from utils.model_util import info, instance2keyword_categories 
from utils.model_util import instance2keyword_detail
from utils.model_util import instance2famines
from utils.map_util import instance2related_locations, field2locations
from misc.models import Keyword, Language,Famine,License
from locations.models import Location
from utilities.models import instance2name, instance2color, instance2icon 
from utilities.models import instance2map_buttons
from utilities.models import instance2names
from partial_date import PartialDateField
from utils.link2embed_source import link2embed_source
from utils.handle_file import handle_file
from utils.instance2countries import instance2countries


def make_simple_model(name):
    '''make a simple model with only a name attribute.'''
    exec('class '+name + '(SimpleModel,info):\n\tpass',globals())

names = 'MusicType,Collection,Rated,Commissioner'
names += ',FilmCompany,FilmType,TargetAudience,PublishingOutlet,Available'
names += ',InfographicType,PictureStoryType,TextType,Publisher,Permission'
names += ',Institution,ProductionStudio,GameType,RecordedspeechType'
names += ',MemorialType,ArtefactType,ImageType,BroadcastingStation'
names = names.split(',')

for name in names:
    make_simple_model(name)

class Source(models.Model):
    '''abstract class all non simple non relational models'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    famines = models.ManyToManyField(Famine, blank=True)
    title_original = models.CharField(max_length=1000,default='')
    title_english = models.CharField(max_length=1000,default='')
    collection = models.ForeignKey(Collection, **dargs)
    publishing_outlet = models.ForeignKey(PublishingOutlet,**dargs)
    available = models.ForeignKey(Available,**dargs)
    permission = models.ForeignKey(Permission,**dargs)
    rated = models.ForeignKey(Rated, **dargs)
    keywords= models.ManyToManyField(Keyword,blank=True)
    description = models.TextField(default='')
    comments = models.TextField(default='')
    date_created = PartialDateField(null=True,blank=True)
    date_released = PartialDateField(null=True,blank=True)
    commissioned_by = models.ForeignKey(Commissioner,**dargs)
    source_link = models.CharField(max_length=1000,default='')
    flag = models.BooleanField(default = False)
    thumbnail = models.ImageField(upload_to='thumbnail/',blank=True,null=True)
    setting = models.ManyToManyField(Location,blank=True)
    release_date_precedent = models.BooleanField(default=False)
    location_field = 'setting'
    country_field = models.CharField(max_length=1000,default='')
    date_field = PartialDateField(null=True,blank=True)
    keyword_category_field = models.CharField(max_length=1000,default='')
    keyword_detail_field = models.CharField(max_length=1000,default='')
    famine_field = models.CharField(max_length=1000,default='')
    loc_ids = models.CharField(max_length=1000,default='')
    license_image = models.ForeignKey(License, 
        related_name='%(app_label)s_%(class)s_license_image',
        **dargs)
    license_thumbnail= models.ForeignKey(License, 
        related_name='%(app_label)s_%(class)s_license_thumbnail',
        **dargs)
    reference= models.TextField(default='')

    class Meta:
        abstract = True

    def save(self,*args,**kwargs):
        super(Source,self).save(*args,**kwargs)
        old_keyword_category_field = self.keyword_category_field
        self.keyword_category_field = instance2keyword_categories(self)
        old_keyword_detail_field = self.keyword_detail_field
        self.keyword_detail_field = instance2keyword_detail(self)
        old_country_field = self.country_field
        self.country_field = instance2countries(self)
        old_date= self.date_field
        self.date_field = self.date
        old_famine_field = self.famine_field
        self.famine_field = instance2famines(self)
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
            super(Source,self).save(*args,**kwargs)

    def __str__(self):
        if self.title_original: return self.title_original
        return self.title_english

    def _set_gps(self):
        self.loc_ids = ''
        ids = [location.pk for location in self.setting.all()]
        if ids: self.loc_ids = ','.join(map(str,ids))

    @property
    def title(self):
        if self.title_english: return self.title_english
        return self.title_original

    @property
    def is_explicit(self):
        if not self.rated: return False
        if self.rated.name == 'explicit': return True
        return False

    @property
    def _pop_up(self):
        app_name, model_name = instance2names(self)
        m = ''
        if self.thumbnail.name:
            m += '<img src="'+self.thumbnail.url
            m +='" width="200" style="border-radius:3%">'
        m += instance2icon(self)
        m += '<p class="h6 mb-0 mt-1" style="color:'+instance2color(self)+';">'
        m += self.title +'</p>'
        m += '<hr class="mt-1 mb-0" style="border:1px solid '
        m += instance2color(self)+';">'
        m += '<p class="mt-2 mb-0">'+self.description+'</p>'

        if hasattr(self,'play_field'):
            link =  getattr(self,getattr(self,'play_field'))
            if link:
                m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" '
                m += 'target="_blank" href="' + link
                m += '" role="button"><i class="fas fa-play"></i></a>'
        m += instance2map_buttons(self)
        return m

    @property
    def has_permission(self):
        if self.permission == None: return False
        return self.permission.name == 'yes'
        

    @property
    def pop_up(self):
        '''can be overwritten by inherited classes to add to the _popup'''  
        return self._pop_up

    @property
    def related_locations(self):
        return instance2related_locations(self) 

    @property
    def latlng(self):
        lf = self.location_field
        location_field = lf if lf else 'setting'
        locations = field2locations(self,self.location_field)
        if locations:
            return [location.gps for location in locations]
        else: return None
    
    @property
    def setting_names(self):
        locations = self.setting.all().order_by('name') 
        if locations: return ', '.join([l.name for l in locations])
        else: return ''

    @property
    def famine_names(self):
        famines= self.famines.all()
        if famines: return ', '.join([f.names_str for f in famines])
        else: return ''

    @property
    def keyword_names(self):
        keywords= self.keywords.all().order_by('name') 
        if keywords: return ', '.join([k.name for k in keywords])
        else: return ''

    @property
    def language_names(self):
        if hasattr(self,'languages_original'): 
            l = getattr(self,'languages_original')
        elif hasattr(self,'languages'): l = getattr(self,'languages')
        else: return ''
        languages=  l.all().order_by('name')  
        if languages:
            return ', '.join( [x.name for x in languages] )
        return ''

    @property
    def identifier(self):
        return self._meta.app_label+'_'+self._meta.model_name+'_'+str( self.pk )

    @property
    def edit_url(self):
        return self._meta.app_label + ':edit_' + self._meta.model_name 

    @property
    def detail_url(self):
        return self._meta.app_label+':detail_'+self._meta.model_name+'_view' 
        
    @property
    def date(self):
        rdp = self.release_date_precedent
        if self.date_released and self.date_created and rdp:
            return self.date_released
        elif self.date_created: return self.date_created
        elif self.date_released: return self.date_released
        else: return ''

    @property
    def year(self):
        date = self.date
        if date == '': return ''
        return date.year

    @property
    def year_range(self):
        if hasattr(self,'_year_range'): return self._year_range
        dates = []
        if self.date_created: dates.append(self.date_created.year)
        if self.date_released: dates.append( self.date_released.year )

        if len(dates) == 0: yr = None
        elif len(dates) == 1: yr = dates * 2
        else: yr = sorted(dates)
        self._year_range = yr
        return self._year_range

    @property
    def image_urls(self):
        '''returns a string of comma seperated urls to images.'''
        o = []
        for field in self._meta.fields:
            if type(field) == ImageField:
                x= getattr(self,field.name)
                if x.name:o.append(x.name)
        return ','.join(o)

    @property
    def info_available(self):
        n = len(self.description) > 165
        t = self.thumbnail
        if (self.setting_names or self.famine_names or self.keyword_names or 
            self.thumbnail or n):
            return True
        else: False
    


class Music(Source,info):
    '''Meta data for songs related to famines.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    lyrics = models.TextField(default='')
    music_video_link = models.CharField(max_length=1000,default='')
    album = models.CharField(max_length=1000,default='')
    performing_artists = models.CharField(max_length=3000,default='')
    composers = models.ManyToManyField(Person,blank=True,
        related_name='music_composer_set')
    music_type = models.ForeignKey(MusicType,**dargs)
    languages = models.ManyToManyField(Language, blank=True)
    music_link = models.CharField(max_length=1000,default='')
    play_field = 'music_video_link'
    
    @property
    def icon(self):
        return 'fas fa-music'

    @property
    def icon_svg(self):
        return '/media/icons/music-solid.svg'

    @property
    def embed_video(self):
        return link2embed_source(self,self.music_video_link)

    @property
    def links(self):
        o = {}
        if self.source_link: o.update({'lyrics':self.source_link})
        if self.music_video_link: o.update({'video':self.music_video_link})
        if self.music_link: o.update({'music':self.music_link})
        if o: return o
        return ''

    class Meta:
        unique_together = [['title_original','date_released']]


class Film(Source, info):
    '''Meta data for movies related to famines.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    languages_original=models.ManyToManyField(Language,blank=True,
        related_name='film_language_original')
    languages_subtitle=models.ManyToManyField(Language,blank=True,
        related_name='film_language_subtitle')
    writers = models.ManyToManyField(Person,blank=True, 
        related_name='film_writers_set')
    directors = models.ManyToManyField(Person,blank=True, 
        related_name='film_directors_set')
    creators = models.ManyToManyField(Person,blank=True,
        related_name='film_creators_set')
    film_companies = models.ManyToManyField(FilmCompany,blank=True,
        related_name='film_film_company')
    locations_shot = models.ManyToManyField(Location,blank=True, 
        related_name='film_location_shot')
    locations_released= models.ManyToManyField(Location,blank=True, 
        related_name='film_location_released')
    target_audience = models.ForeignKey(TargetAudience,**dargs)
    film_type = models.ForeignKey(FilmType,**dargs)
    video_link = models.CharField(max_length=1000,default='')
    video_part_link = models.CharField(max_length=1000,default='')
    play_field = 'video_link'

    @property
    def icon(self):
        return 'fa fa-film'

    @property
    def icon_svg(self):
        return '/media/icons/film-solid.svg'

    @property
    def embed_video(self):
        p,s,t = self.video_link, self.video_part_link, self.source_link
        return link2embed_source(self,p,s,t) 

    @property
    def links(self):
        o = {}
        if self.source_link: o.update({'information':self.source_link})
        if self.video_link: o.update({'video':self.video_link})
        if self.video_part_link: o.update({'clip':self.video_part_link})
        if o: return o
        return ''

    class Meta:
        unique_together = [['title_original','date_released']]
    

class Artefact(Source, info):
    '''Meta data for material artefacts related to famines.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    artefact_type = models.ForeignKey(ArtefactType,**dargs)
    locations = models.ManyToManyField(Location,blank=True, 
        related_name='artefact_locations')
    creators = models.ManyToManyField(Person,blank=True, 
        related_name='artefact_creators_set')
    image_file = models.ImageField(upload_to='artefact/',blank=True,null=True)
    location_field = 'locations'
    image_filename = models.CharField(max_length=500,default='',blank=True,
        null=True)

    @property
    def icon(self):
        return 'fas fa-utensil-spoon'

    @property
    def icon_svg(self):
        return '/media/icons/spoon-solid.svg'

    @property
    def links(self):
        o = {}
        if self.source_link: o.update({'source':self.source_link})
        if self.image_file: o.update({'image':self.image_file.url})
        if o: return o
        return ''

    class Meta:
        unique_together = [['title_original','date_created','image_filename']]


class Image(Source, info):
    '''Meta data for Images related to famines.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    image_type = models.ForeignKey(ImageType,**dargs)
    locations = models.ManyToManyField(Location,blank=True, 
        related_name='image_locations')
    creators = models.ManyToManyField(Person,blank=True, 
        related_name='image_creators_set')
    image_file = models.ImageField(upload_to='image/',blank=True,null=True)
    location_field = 'locations'
    image_filename = models.CharField(max_length=500,default='',
        blank=True,null=True)

    @property
    def icon(self):
        return 'fas fa-image'

    @property
    def icon_svg(self):
        return '/media/icons/image-solid.svg'

    @property
    def creator_occupation_name(self):
        name = 'Creator:'
        if not self.image_type: return name
        if self.image_type.name == 'drawings':name = 'Drawer:'
        if self.image_type.name == 'engravings':name = 'Engrapher:'
        if self.image_type.name == 'Etching':name = 'Graphic artist:'
        if self.image_type.name == 'lithographs':name = 'Graphic artist:'
        if self.image_type.name == 'paintings':name = 'Painter:'
        if self.image_type.name == 'poster':name = 'Graphic artist:'
        if self.image_type.name == 'photograph':name = 'Photographer:'
        if self.image_type.name == 'woodcuts':name = 'Graphic artist:'
        return name

    @property
    def links(self):
        o = {}
        if self.source_link: o.update({'source':self.source_link})
        if self.image_file: o.update({'image':self.image_file.url})
        if o: return o
        return ''

    @property
    def pop_up(self):
        m = self._pop_up
        if self.image_file.name:
            m += '<a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" '
            m += 'target="_blank" href='
            m += self.image_file.url
            m += 'role="button"><i class="fas fa-play"></i></a>'
        return m

    class Meta:
        unique_together = [['title_original','image_filename']]

    
class Infographic(Source,info):
    '''Meta data for infographics related to famines.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    infographic_type = models.ForeignKey(InfographicType,**dargs)
    creators = models.ManyToManyField(Person,blank=True, 
        related_name='infographic_creators_set')
    image_file = models.ImageField(upload_to='infographic/',blank=True,null=True)
    languages = models.ManyToManyField(Language, blank=True)
    locations = models.ManyToManyField(Location,blank=True, 
        related_name='infographic_locations')
    location_field = 'locations'
    image_filename = models.CharField(max_length=500,default='',blank=True,
        null=True)

    @property
    def icon(self):
        return 'fas fa-chart-area'

    @property
    def icon_svg(self):
        return '/media/icons/chart-area-solid.svg'

    @property
    def links(self):
        o = {}
        if self.source_link: o.update({'source':self.source_link})
        if self.image_file: o.update({'image':self.image_file.url})
        if o: return o
        return ''

    class Meta:
        unique_together = [['title_original','image_filename']]


class PictureStory(Source,info):
    '''Meta data for picturestories (comics / graphic novels) related to famines.
    '''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    picture_story_type = models.ForeignKey(PictureStoryType,**dargs)
    authors = models.ManyToManyField(Person,blank=True, 
        related_name='picture_story_author_set')
    artists = models.ManyToManyField(Person,blank=True, 
        related_name='picture_story_artist_set')
    translators= models.ManyToManyField(Person,blank=True, 
        related_name='picture_story_translator_set')
    publishers = models.ManyToManyField(Publisher,blank=True,
        related_name='picture_story_publisher_set')
    languages = models.ManyToManyField(Language, blank=True)
    image_file = models.ImageField(upload_to='picturestory/',blank=True,
        null=True)
    excerpt_file = models.FileField(upload_to='picturestory/',blank=True,
        null=True)
    locations = models.ManyToManyField(Location,blank=True, 
        related_name='picture_story_locations')
    location_field = 'locations'
    image_filename = models.CharField(max_length=500,default='',
        blank=True,null=True)

    @property
    def links(self):
        o = {}
        if self.source_link: o.update({'source':self.source_link})
        if self.image_file: o.update({'image':self.image_file.url})
        if self.excerpt_file: o.update({'excerpt':self.excerpt_file.url})
        if o: return o
        return ''

    @property
    def picture_story(self):
        return handle_file(self,self.excerpt_file)


    @property
    def icon(self):
        return 'fas fa-book-open'

    @property
    def icon_svg(self):
        return '/media/icons/book-open-solid.svg'

    class Meta:
        unique_together = [['title_original','image_filename']]

    
class Text(Source,info):
    '''Meta data for texts related to famines.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    text_type = models.ForeignKey(TextType,**dargs)
    authors = models.ManyToManyField(Person,blank=True,
        related_name='text_author_set')
    institution_authors= models.ManyToManyField(Institution,blank=True,
        related_name='text_author_set')
    editors = models.ManyToManyField(Person,blank=True,
        related_name='text_editor_set')
    translators = models.ManyToManyField(Person,blank=True,
        related_name='text_translator_set')
    publishers = models.ManyToManyField(Publisher,blank=True,
        related_name='text_publisher')
    languages = models.ManyToManyField(Language, blank=True)
    original_languages= models.ManyToManyField(Language, blank=True,
        related_name='text_original_languages')
    text_file = models.FileField(upload_to='text/',blank=True,null=True)
    excerpt_file = models.FileField(upload_to='text/',blank=True,null=True)
    locations = models.ManyToManyField(Location,blank=True, 
        related_name='text_locations')
    location_field = 'locations'

    @property
    def icon(self):
        return 'fas fa-file-alt'

    @property
    def icon_svg(self):
        return '/media/icons/file-lines-solid.svg'

    @property
    def links(self):
        o = {}
        if self.source_link: o.update({'source':self.source_link})
        if self.text_file: o.update({'text':self.text_file.url})
        if self.excerpt_file: o.update({'excerpt':self.excerpt_file.url})
        if o: return o
        return ''

    @property
    def text(self):
        return handle_file(self,self.text_file)
        
    
    class Meta:
        unique_together = [['title_original','date_released']]



class Videogame(Source,info):
    '''Meta data for texts related to famines.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    game_type = models.ForeignKey(GameType,**dargs)
    production_studio= models.ManyToManyField(ProductionStudio,blank=True,
        related_name='videogame_productionstudio_set')
    languages_original=models.ManyToManyField(Language,blank=True,
        related_name='videogame_language_original')
    languages_subtitle=models.ManyToManyField(Language,blank=True,
        related_name='videogame_language_subtitle')
    video_link = models.CharField(max_length=1000,default='')
    
    @property
    def icon(self):
        return 'fas fa-gamepad'

    @property
    def icon_svg(self):
        return '/media/icons/gamepad-solid.svg'

    @property
    def embed_video(self):
        return link2embed_source(self,self.video_link) 

    @property
    def links(self):
        o = {}
        if self.source_link: o.update({'source':self.source_link})
        if self.video_link: o.update({'video':self.video_link})
        if o: return o
        return ''

    class Meta:
        unique_together = [['title_original','date_released']]


class Recordedspeech(Source,info):
    '''Meta data for texts related to famines.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    recordedspeech_type= models.ForeignKey(RecordedspeechType,**dargs)
    creators = models.ManyToManyField(Person,blank=True,
        related_name='recordedspeech_creators_set')
    speakers = models.ManyToManyField(Person,blank=True,
        related_name='recordedspeech_speakers_set')
    broadcasting_station= models.ForeignKey(BroadcastingStation,**dargs)
    languages=models.ManyToManyField(Language,blank=True,
        related_name='recordedspeech_language')
    audio_link = models.CharField(max_length=1000,default='')
    locations_recorded= models.ManyToManyField(Location,blank=True, 
        related_name='recordedspeech_location_recorded')

    @property
    def icon(self):
        return 'far fa-comments'

    @property
    def icon_svg(self):
        return '/media/icons/comments-regular.svg'

    @property
    def links(self):
        o = {}
        if self.source_link: o.update({'source':self.source_link})
        if self.audio_link: o.update({'audio':self.audio_link})
        if o: return o
        return ''

    class Meta:
        unique_together = [['title_original','date_released']]
    

class Memorialsite(Source,info):
    '''Meta data for texts related to famines.'''
    dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}
    memorial_type= models.ForeignKey(MemorialType,**dargs)
    creators = models.ManyToManyField(Person,blank=True,
        related_name='memorialsite_creators_set')
    artists= models.ManyToManyField(Person,blank=True,
        related_name='memorialsite_artists_set')
    image_file1 = models.ImageField(upload_to='memorialsite/',blank=True,
        null=True)
    image_file2 = models.ImageField(upload_to='memorialsite/',blank=True,
        null=True)
    image_file3 = models.ImageField(upload_to='memorialsite/',blank=True,
        null=True)
    donor_persons= models.ManyToManyField(Person,blank=True,
        related_name='memorialsite_person_donors_set')
    donor_institutions= models.ManyToManyField(Institution,blank=True,
        related_name='memorialsite_institution_donors_set')
    commissioning_persons= models.ManyToManyField(Person,blank=True,
        related_name='memorialsite_person_commissioning_set')
    commissioning_institutions= models.ManyToManyField(Institution,blank=True,
        related_name='memorialsite_institution_commissioning_set')
    languages=models.ManyToManyField(Language,blank=True,
        related_name='memorialsite_language')
    locations= models.ManyToManyField(Location,blank=True, 
        related_name='memorialsite_location_recorded')
    video_link = models.CharField(max_length=1000,default='')
    location_field = 'locations'

    @property
    def icon(self):
        return 'fas fa-monument'

    @property
    def icon_svg(self):
        return '/media/icons/monument-solid.svg'

    @property
    def links(self):
        o = {}
        if self.image_file1: o.update({'image 1':self.image_file1.url})
        if self.image_file2: o.update({'image 2':self.image_file2.url})
        if self.image_file3: o.update({'image 3':self.image_file3.url})
        if self.video_link: o.update({'video':self.video_link})
        if self.source_link: o.update({'source':self.source_link})
        if o: return o
        return ''

    @property
    def image_count(self):
        a = bool(self.image_file1) 
        b = bool(self.image_file2)
        c = bool(self.image_file3)
        return sum([a,b,c])
    
    class Meta:
        unique_together = [['title_original','date_released']]

