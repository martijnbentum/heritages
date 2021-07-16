from django.test import TestCase
from sources.models import Source, Music

# Create your tests here.
class SourceTestCase(TestCase):
	def setUp(self):
		Music.objects.create(title_original = 'original',title_english = 'english')
		Music.objects.create(title_english = 'only english')
		Music.objects.create(title_original =  'pop up') # should be third to be created for assert
		Music.objects.create(title_original =  'pop up and play', music_video_link = 'link') # 4!


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

