from django.core.management.base import BaseCommand
from django.db import connection 
from utils import model_util

'''
updated info stored instances from other instances
this info is stored to speed up search queries
this can get out of date if the instances are not saved after
changes are made to the linked other instances
'''


class Command(BaseCommand):

	def handle(self, *args, **options):
		print('updating info fields on all instances')
		print('based on linked instances')
		model_util.update_all_instances(remove_cruds=True)
		print('done updating')

