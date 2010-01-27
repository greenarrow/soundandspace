from django.core.management.base import BaseCommand
from soundandspace import filesync


class Command(BaseCommand):
	def handle(self, **options):
		filesync.scan_folders()











