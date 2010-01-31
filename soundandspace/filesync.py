from soundandspace import models
import os, datetime, threading, pyinotify



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


class Watcher(threading.Thread):
	
	def watch(self, blocking=True):
		if blocking:
			self.run()
		else:
			self.start()
		
	def run(self):
		wm = pyinotify.WatchManager()
		self.notifier = pyinotify.Notifier( wm, HandleEvents() )
		watches = []
		
		for folder in models.WatchFolder.objects.filter(watch=True):
			
			print "watching %s" % folder.path
			watch = wm.add_watch(folder.path, mask, rec=True)
			watches.append(watch)
		
		while self.alive:
			try:
				# process the queue of events as explained above
				self.notifier.process_events()
				while self.notifier.check_events():  #loop in case more events appear while we are processing
					self.notifier.read_events()
					self.notifier.process_events()
		
			except KeyboardInterrupt:
				# destroy the inotify's instance on this interrupt (stop monitoring)
				self.notifier.stop()
				break
	
	def terminate(self):
		self.alive = False
		self.notifier.stop()


def check_node_tree(node, nodes_removed):
	child_nodes = models.FileNode.objects.filter(parent=node)
	
	for cn in child_nodes:
		check_node_tree(cn, nodes_removed)
	
	if not node.check_exists_filesystem():
		node.delete()
		nodes_removed.append(node)
	

def scan_folders(verbose=True):
	if verbose:
		print "Starting Scan"
	for folder in models.WatchFolder.objects.filter():
		
		if verbose:
			print "scanning %s - node %s" % (folder.path, folder.root_node)
		
		nodes_added = []
		
		# Check to see if the watch folder has a root file node. If it does not then create it.		
		if folder.root_node == None:
			created = datetime.datetime.now()
			node = models.FileNode(name="", parent=None, created=created, updated=created)
			node.save()
			nodes_added.append(node)
			folder.root_node = node
			folder.save()
		
		# Walk through the entire path of the watch folder on the disk.
		for path, dirs, files in os.walk(folder.path):
			
			relative_path = path[ len(folder.path) + 1: ]
			
			# For every file and directory check if a corresponding node exists in the db. If it does not then create one.
			for item in dirs + files:
				full_path = os.path.join(relative_path, item)
				node = folder.get_node(full_path)
				if node == None:
					if verbose:
						print "..create node", relative_path, item
					new_node = folder.create_node(relative_path, item)
					nodes_added.append(new_node)
		
		
		nodes_removed = []
		check_node_tree(folder.root_node, nodes_removed)
		
		nodes_modified = []
		
		created = datetime.datetime.now()
		log = u"Added %d, Modified %d, Removed %d\nAdded:\n%s\nModifed:\n%s\nRemoved:\n%s" % ( len(nodes_added), len(nodes_modified), len(nodes_removed), " ".join( [node.name for node in nodes_added] ), " ".join( [node.name for node in nodes_modified] ), " ".join( [node.name for node in nodes_removed] ) )
		synclog = models.SyncLog(created=created, log=log)
		synclog.save()




