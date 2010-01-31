from django.core.management.base import BaseCommand
from soundandspace import models


#mask = pyinotify.EventsCodes.ALL_EVENTS
mask = pyinotify.EventsCodes.IN_CREATE | pyinotify.EventsCodes.IN_DELETE | pyinotify.EventsCodes.IN_CLOSE_WRITE | pyinotify.EventsCodes.IN_MOVE_SELF | pyinotify.EventsCodes.IN_MOVED_FROM | pyinotify.EventsCodes.IN_MOVED_TO


class Command(BaseCommand):
	def handle(self, **options):
		print "sd"
		
		watcher = filesync.Watcher()
		watcher.watch(blocking=True)











