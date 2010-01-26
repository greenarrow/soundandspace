from django.core.management.base import BaseCommand
from soundandspace import models
import pyinotify, os


#mask = pyinotify.EventsCodes.ALL_EVENTS
mask = pyinotify.EventsCodes.IN_CREATE | pyinotify.EventsCodes.IN_DELETE | pyinotify.EventsCodes.IN_CLOSE_WRITE | pyinotify.EventsCodes.IN_MOVE_SELF | pyinotify.EventsCodes.IN_MOVED_FROM | pyinotify.EventsCodes.IN_MOVED_TO



class HandleEvents(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		if "IN_ISDIR" in event.event_name:
			print "Create: %s" %  os.path.join(event.path, event.name)
		
	def process_IN_DELETE(self, event):
		print "Remove: %s" %  os.path.join(event.path, event.name)
	
	def process_IN_CLOSE_WRITE(self, event):
		print "Write: %s" %  os.path.join(event.path, event.name)
	
	def process_IN_MOVE_SELF(self, event):
		print event.name
		if event.name != "":
			print "Move: %s" %  os.path.join(event.path, event.name)
	
	def process_IN_MOVED_FROM(self, event):
		if "IN_ISDIR" in event.event_name:
			print "Moved from (gone): %s" %  os.path.join(event.path, event.name)
		else:
			print "Moved from (gone): %s" %  os.path.join(event.path, event.name)
	
	def process_IN_MOVED_TO(self, event):
		if "IN_ISDIR" in event.event_name:
			print "Moved to (new): %s" %  os.path.join(event.path, event.name)
		else:
			print "Moved to (new): %s" %  os.path.join(event.path, event.name)



class Command(BaseCommand):
	def handle(self, **options):
		print "sd"
		
		wm = pyinotify.WatchManager()
		notifier = pyinotify.Notifier( wm, HandleEvents() )
		watches = []
		
		for folder in models.WatchFolder.objects.filter(watch=True):
			
			print "watching %s" % folder.path
			watch = wm.add_watch(folder.path, mask, rec=True)
			watches.append(watch)
		
		while True:
			try:
				# process the queue of events as explained above
				notifier.process_events()
				while notifier.check_events():  #loop in case more events appear while we are processing
					notifier.read_events()
					notifier.process_events()
		
			except KeyboardInterrupt:
				# destroy the inotify's instance on this interrupt (stop monitoring)
				notifier.stop()
				break











