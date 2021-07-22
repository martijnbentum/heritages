from django.test import TestCase
from django.db import IntegrityError
from sources.models import Source, Music, MusicType, FilmCompany,TargetAudience,Film, FilmType
from sources.models import Artefact, ArtefactType, Image, ImageType, Infographic,InfographicType
from sources.models import Videogame, GameType, Recordedspeech, RecordedspeechType
from sources.models import Memorialsite, MemorialType, Text, TextType
from persons.models import Person
from misc.models import Language,Famine,FamineName,Keyword
from partial_date import PartialDate
from locations.models import Location

import random

# Create your tests here.

class Helperdata():
	def __init__(self):
		self.make_data()

	def make_data(self):
		self.language_names = 'dutch,english,french,italian,russian,japanese,mandarin'.split(',')
		self.location_names = 'rome,london,amsterdam,madrid,berlin,bern,paris,washington'.split(',')
		self.person_names = 'james smith,amy,michael,david,lewis,harry,nina,larry jones'.split(',')
		self.keyword_names = 'hot,cold,high,low,strong,weak,corrupt,fair,war,peace'.split(',')
		self.famine_names = 'irish,hungerwinter,nuclear,holodomore'.split(',')
		if not self._data_already_made(): 
			for l in self.language_names:
				Language.objects.create(name = l)
			for l in self.location_names:
				lat,lng = _make_random_float(), _make_random_float()
				Location.objects.create(name = l, latitude = lat, longitude = lng )
			for p in self.person_names:
				Person.objects.create(name = p)
			for name in self.famine_names:
				fn = FamineName.objects.create(name = name)
				f = Famine.objects.create(description= name)
				f.names.add(fn)
			for k in self.keyword_names:
				Keyword.objects.create(name = k)

	def _data_already_made(self):
		l = Language.objects.all()
		n = l.count()
		if n == 0: return False
		if n != len(self.language_names): 
			print(n,'languages not equal to n language_names',len(self.language_names))
		return True

	
	def random_instance(self,model,n = 1):
		x = list(model.objects.all())
		if n > len(x): n = len(x)
		return random.sample(x,n)

	def instance(self,model,n = 1):
		x = list(model.objects.all())
		if n > len(x): n = len(x)
		return x[:n]

	def date(self):
		return PartialDate(str(random.randint(1,2020)))
		
		
def _make_random_float(lower=0, upper=90,percision = 3):
	f = random.randint(lower,upper) + random.random()
	return round(f,percision)




class SourceTestCase(TestCase):
	'''test the abstract class source.
	main models in source inherit from this class
	latlng, related_locations, image_urls are untested methods  
	'''

	def setUp(self):
		h = Helperdata()
		d1 = PartialDate('1979')
		d2 = PartialDate('1989')
		Music.objects.create(title_original = 'original',title_english = 'english')
		Music.objects.create(title_english = 'only english',date_created =d1)
		Music.objects.create(title_original =  'pop up') # should be third to be created for assert
		Music.objects.create(title_original =  'pop up and play', music_video_link = 'link') # 4!
		Music.objects.create(title_original =  'badaboem', date_released= d2) 
		Music.objects.create(title_original =  'extra') 
		mt = MusicType.objects.create(name='jazz')
		m = Music.objects.create(
			title_original = 'the song',
			music_type = mt,
			date_created = d1,
			date_released = d2,
			description = lorem
		)
		m.composers.add(*h.instance(Person,1))
		m.languages.add(*h.instance(Language,2))
		m.famines.add(*h.instance(Famine,4))
		m.keywords.add(*h.instance(Keyword,5))
		m.setting.add(*h.instance(Location,3))
		m = Music.objects.create(
			title_original='when song',
			date_created = d1, 
			date_released= d2,
			release_date_precedent = True 
		)

	def test_date(self):
		create_date = PartialDate('1979')
		release_date = PartialDate('1989')
		both = Music.objects.get(title_original='the song')
		precedent= Music.objects.get(title_original='when song')
		only_create =Music.objects.get(title_original='only english')
		only_release =Music.objects.get(title_original='only english')
		self.assertEqual(both.date,create_date)
		self.assertEqual(precedent.date,release_date)
		self.assertEqual(only_create.date,create_date)
		self.assertEqual(only_release.date,release_date)
		
	def test_setting_names(self):	
		'''setting names is a property that returns a comma seperated string of location names.'''
		h = Helperdata()
		l = ', '.join([l.name for l in h.instance(Location,3)])
		m = Music.objects.get(title_original='the song')
		self.assertEqual(m.setting_names,l)

	def test_famine_names(self):
		h = Helperdata()
		l = ', '.join([f.names_str for f in h.instance(Famine,4)])
		m = Music.objects.get(title_original='the song')
		self.assertEqual(m.famine_names,l)
			
	def test_keyword_names(self):	
		h = Helperdata()
		l = ', '.join([l.name for l in h.instance(Keyword,5)])
		m = Music.objects.get(title_original='the song')
		self.assertEqual(m.keyword_names,l)

	def test_language_names(self):
		h = Helperdata()
		l = ', '.join([l.name for l in h.instance(Language,2)])
		m = Music.objects.get(title_original='the song')
		self.assertEqual(m.language_names,l)

	def test_identifier(self):
		m = Music.objects.get(title_original='the song')
		pk = str(m.pk)
		self.assertEqual(m.identifier, 'source_music_' + pk)

	def test_edit_url(self):
		m = Music.objects.get(title_original='the song')
		self.assertEqual(m.edit_url, 'source:edit_music')

		


	def test_title_original_before_title_english(self):
		o= Music.objects.get(title_english = 'english')
		e= Music.objects.get(title_english = 'only english')
		self.assertEqual(o.title, 'original')
		self.assertEqual(o.title_english, 'english')
		self.assertEqual(e.title, 'only english')
		
	def test_pop_up(self):	
		self.maxDiff = None
		p = Music.objects.get(title_original= 'pop up')
		pop_up = '''<i class="fas fa-music fa-lg mt-2" aria-hidden="true"></i><p class="h6 mb-0 mt-1" style="color:black;">pop up</p><hr class="mt-1 mb-0" style="border:1px solid black;"><p class="mt-2 mb-0"></p><a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href=/sources/edit_music/3/ role="button"><i class="far fa-edit"></i></a><a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href=/locations/show_links/sources/music/3/ role="button"><i class="fas fa-project-diagram"></i></a>'''
		self.assertEqual(p._pop_up,pop_up)
		p = Music.objects.get(title_original= 'pop up and play')
		pop_up = '''<i class="fas fa-music fa-lg mt-2" aria-hidden="true"></i><p class="h6 mb-0 mt-1" style="color:black;">pop up and play</p><hr class="mt-1 mb-0" style="border:1px solid black;"><p class="mt-2 mb-0"></p><a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" target="_blank" href="link" role="button"><i class="fas fa-play"></i></a><a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href=/sources/edit_music/4/ role="button"><i class="far fa-edit"></i></a><a class = "btn btn-link btn-sm mt-1 pl-0 text-dark" href=/locations/show_links/sources/music/4/ role="button"><i class="fas fa-project-diagram"></i></a>'''
		self.assertEqual(p._pop_up,pop_up)
		self.maxDiff = 50

	def test_identifier(self):
		m = Music.objects.get(pk = 1)
		self.assertEqual(m.identifier,'sources_music_1')

	def test_edit_url(self):
		m = Music.objects.get(pk = 1)
		self.assertEqual(m.edit_url,'sources:edit_music')

	def test_date(self):
		m = Music.objects.get(title_original = 'badaboem')
		self.assertEqual(m.date_released.name, '1989')


class MusicTestCase(TestCase):
	def setUp(self):
		p = Person.objects.create(name='peter smith')
		mt = MusicType.objects.create(name='jazz')
		l = Language.objects.create(name='English')
		d = PartialDate('1999')
		self.unique_dict = {'title_original':'this song','date_released':d}
		m = Music.objects.create(
			title_english='song english',
			lyrics='hello\nhello\nbye',
			album='album',
			performing_artists='artist',
			music_link = 'spotify',
			music_video_link = 'youtube',
			music_type = mt,
			**self.unique_dict
		)
		m.composers.add(p)
		unique_together = [['title_original','date_released']]
		
	def test_unique_together(self):
		with self.assertRaises(IntegrityError) as context:
			Music.objects.create(**self.unique_dict)


class FilmTestCase(TestCase):
	def setUp(self):
		p1 = Person.objects.create(name='james smith')
		p2 = Person.objects.create(name='amy smith')
		ft = FilmType.objects.create(name='comedy')
		l1 = Language.objects.create(name='Dutch')
		l2 = Language.objects.create(name='French')
		d = PartialDate('1989')
		loc1 = Location.objects.create(name='Amsterdam')
		loc2 = Location.objects.create(name='Haarlem')
		fc = FilmCompany.objects.create(name='heyhomovie')
		ta = TargetAudience.objects.create(name='elderly')
		self.unique_dict = {'title_original':'this film','date_released':d}
		f = Film.objects.create(
			target_audience=ta,
			video_part_link = 'youtube',
			film_type = ft,
			**self.unique_dict,
		)
		f.languages_original.add(l1)	
		f.languages_subtitle.add(l2)
		f.locations_shot.add(loc1)
		f.locations_shot.add(loc2)
		f.locations_released.add(loc2)
		f.film_companies.add(fc)
		f.writers.add(p1)
		f.writers.add(p2)
		f.directors.add(p2)
		f.creators.add(p2)
		unique_together = [['title_original','date_released']]

	def test_unique_together(self):
		with self.assertRaises(IntegrityError) as context:
			Film.objects.create(**self.unique_dict)


class ArtefactTestCase(TestCase):
	def setUp(self):
		at = ArtefactType.objects.create(name='utensil')
		d = PartialDate('1901')
		self.unique_dict={'title_original':'spoon','image_filename':'image_name','date_created':d}
		a = Artefact.objects.create(
			artefact_type = at,
			**self.unique_dict,
		)
		unique_together = [['title_original','date_created','image_filename']]

	def test_unique_together(self):
		with self.assertRaises(IntegrityError) as context:
			Artefact.objects.create(**self.unique_dict)


class ImageTestCase(TestCase):
	def setUp(self):
		self.unique_dict = {'title_original':'the house','image_filename':'image_name'}
		it = ImageType.objects.create(name = 'painting')
		d = PartialDate('1701')
		i = Image.objects.create(
			date_created = d,
			image_type = it,
			**self.unique_dict,
		)
		unique_together = [['title_original','image_filename']]

	def test_unique_together(self):
		with self.assertRaises(IntegrityError) as context:
			Image.objects.create(**self.unique_dict)
		

class InfographicTestCase(TestCase):
	def setUp(self):
		self.unique_dict = {'title_original':'the graph','image_filename':'image_name'}
		it = InfographicType.objects.create(name = 'barplot')
		d = PartialDate('1601')
		i = Infographic.objects.create(
			date_created = d,
			infographic_type = it,
			**self.unique_dict,
		)
		unique_together = [['title_original','image_filename']]

	def test_unique_together(self):
		with self.assertRaises(IntegrityError) as context:
			Infographic.objects.create(**self.unique_dict)

class TextTestCase(TestCase):
	def setUp(self):
		tt = TextType.objects.create(name = 'novel')
		d = PartialDate('1931')
		self.unique_dict = {'title_original':'the story','date_released':d}
		t = Text.objects.create(
			text_type= tt,
			**self.unique_dict,
		)
		unique_together = [['title_original','date_released']]

	def test_unique_together(self):
		with self.assertRaises(IntegrityError) as context:
			Text.objects.create(**self.unique_dict)


class VideogameTestCase(TestCase):
	def setUp(self):
		gt = GameType.objects.create(name = 'strategy')
		d = PartialDate('1991')
		self.unique_dict = {'title_original':'the graph','date_released':d}
		v = Videogame.objects.create(
			game_type= gt,
			**self.unique_dict,
		)
		unique_together = [['title_original','date_released']]

	def test_unique_together(self):
		with self.assertRaises(IntegrityError) as context:
			Videogame.objects.create(**self.unique_dict)


class RecordedspeechTestCase(TestCase):
	def setUp(self):
		p1 = Person.objects.create(name='jamy io')
		p2 = Person.objects.create(name='james o')
		rt = RecordedspeechType.objects.create(name = 'discussion')
		d = PartialDate('2001')
		self.unique_dict = {'title_original':'the talk','date_released':d}
		v = Recordedspeech.objects.create(
			recordedspeech_type= rt,
			**self.unique_dict,
		)
		v.creators.add(p1)
		v.creators.add(p1,p2)
		v.speakers.add(p2)
		unique_together = [['title_original','date_released']]

	def test_unique_together(self):
		with self.assertRaises(IntegrityError) as context:
			Recordedspeech.objects.create(**self.unique_dict)


class MemorialsiteTestCase(TestCase):
	def setUp(self):
		mt = MemorialType.objects.create(name = 'statue')
		d = PartialDate('1291')
		self.unique_dict = {'title_original':'the person','date_released':d}
		v = Memorialsite.objects.create(
			memorial_type= mt,
			**self.unique_dict,
		)
		unique_together = [['title_original','date_released']]

	def test_unique_together(self):
		with self.assertRaises(IntegrityError) as context:
			Memorialsite.objects.create(**self.unique_dict)




lorem = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam elit enim, euismod sed pharetra sit amet, volutpat a ipsum. Morbi mattis luctus luctus. In hac habitasse platea dictumst. Cras nec euismod dolor. Integer a gravida magna, at porta orci. Donec vel quam vel nibh porta sagittis at id eros. Donec commodo sit amet neque non molestie. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Phasellus eleifend volutpat enim, convallis pellentesque ante sollicitudin porta. Nunc arcu risus, rhoncus quis lectus non, tempor finibus felis. Mauris rhoncus magna vel diam cursus elementum.

Proin dignissim blandit tellus nec ultrices. Mauris ultrices iaculis arcu et porta. Cras auctor nunc ut urna cursus, at lacinia velit vehicula. In quis aliquet orci. Quisque dignissim eleifend volutpat. Vivamus gravida elit sit amet elit blandit, ac pellentesque tortor commodo. Morbi bibendum pharetra blandit. Duis in ipsum porta, efficitur felis vel, vehicula purus. Vestibulum eget sapien at lacus placerat viverra. Suspendisse erat elit, pellentesque sit amet dapibus eu, tincidunt ut leo. Suspendisse lacus quam, placerat nec augue quis, malesuada dignissim diam. Integer viverra arcu quis maximus porttitor. Donec vestibulum mauris eget justo porttitor ultricies. Cras enim est, interdum a pretium a, lacinia vel nunc. Suspendisse tempor risus mauris, et scelerisque nunc euismod lacinia.
'''

