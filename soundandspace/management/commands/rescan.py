from django.core.management.base import BaseCommand
from soundandspace import models
import os, datetime


class Command(BaseCommand):
	def handle(self, **options):
		
		print "scan"
		for folder in models.WatchFolder.objects.filter(watch=True):
			
			print "scanning %s - node %s" % (folder.path, folder.root_node)
			
			if folder.root_node == None:
				created = datetime.datetime.now()
				node = models.FileNode(name="", parent=None, created=created, updated=created)
				node.save()
				folder.root_node = node
				folder.save()
			
			for path, dirs, files in os.walk(folder.path):
				
				relative_path = path[ len(folder.path) + 1: ]
				
				print relative_path, dirs, files
				#models.FileNode.objects.filter(name
				"""
				for d in dirs:
					print path, d
					try:
						# unicode may raise exception on bad file characters
						p = FileNode(path = unicode( path[ len(search_path) - 1: ] ), name = d, node_type = constants.NODE_FOLDER)
						p.save()
					except:
						print "Error making node"
						errors += 1
						
				
				for f in files:
					print path[ len(search_path): ], f
					try:
						p = FileNode(path = unicode( path[ len(search_path) - 1: ] ), name = f, node_type = constants.NODE_FILE)
						p.save()
					except:
						print "Error making node"
						errors += 1
					else:
						file_count += 1
				"""











