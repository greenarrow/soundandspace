from django.db import models
import datetime, os



class FileNode(models.Model):
	"""Node used in database representation of filesystem. May represent file or folder"""
	
	# The individual file / folder name, not the full path
	name = models.CharField(max_length=255)
	
	# Parent node, i.e. the folder above
	parent = models.ForeignKey("self", blank=True, null=True)
	
	# Set True if the node is a directory
	directory = models.BooleanField()
	
	# TODO: Is there some handle that can be used to updated these automatically?
	created = models.DateTimeField()
	updated = models.DateTimeField()
	
	
	def check_exists_filesystem(self):
		"""Returns True if the path specified by a node actually exists on the filesystem"""
		return os.path.exists( self.get_absolute_path() )
	
	
	def get_relative_path(self, target=None):
		"""Returns the file path of the node relative to the root node of the watch folder, or if target is supplied; the specific target folder."""
		node = self
		path = self.name
		
		# Traverse back up the tree collecting the path until we hit either the watch folder root node (has no parent) or target node (if specified)
		while node.parent != None and node != target:
			node = node.parent
			path = os.path.join(node.name, path)
		
		# If we were going for a target and we found it return the collected path
		if node == target:
			return path
		
		# If we were going for the root node check we found it and if so return the collected path
		elif target == None:
			results = WatchFolder.objects.filter(root_node=node)
			
			if len(results):
				return path
		
		raise LookupError
	
	
	def get_absolute_path(self):
		"""Returns the absolute path of a node on the filesystem"""
		node = self
		path = self.name
		while node.parent != None:
			node = node.parent
			path = os.path.join(node.name, path)
		
		results = WatchFolder.objects.filter(root_node=node)
		
		if len(results):
			path = os.path.join( results[0].path, path )
			return path
		else:
			raise LookupError
	
	
	def get_child_nodes(self):
		"""Returns all of the child nodes of this node"""
		return FileNode.objects.filter(parent=self)
	
	
	def get_watch_folder(self):
		""""""
		if self.parent == None:
			results = WatchFolder.objects.filter(root_node=self)
			if len(results) == 1:
				return results[0]
		raise LookupError
	
	
	def is_empty(self):
		"""Returns True if the node has no child nodes"""
		return len( self.get_child_nodes() ) == 0
	
	
	def is_root_node(self):
		"""Returns True if the node is the root node for a watch folder. A root node has path equal to the path of the watch folder."""
		try:
			self.get_watch_folder()
		except LookupError:
			return False
		
		return True
	
	
	def remove_child_node_tree(self):
		"""Delete the full tree of nodes from each of the current node's child nodes. Does not delete the current node itself."""
		child_nodes = FileNode.objects.filter(parent=self)
		for node in child_nodes:
			node.remove_child_node_tree()
		child_nodes.delete()
	
	
	def __unicode__(self):
		#return u"%s - %s" % ( str(self.id), str(self.name) )
		return u"%s" % ( str(self.id) )
	
	
	class Meta:
		# Show the directories first.
		ordering = ('-directory', 'name')


class WatchFolder(models.Model):
	"""A folder that soundandspace will scan and show store in the database, then watch for changes."""
	
	# The user displayed name for the folder
	name = models.CharField(max_length=255)
	
	# The full path on the filesystem of the folder
	path = models.CharField(max_length=1000)
	
	# Set True if the folder is to be watched for changes by the daemon
	watch = models.BooleanField()
	
	# The node tree representation of the filesystem branches off from the WatchFolder's root node.
	root_node = models.ForeignKey(FileNode, blank=True, null=True)
	
	
	def get_node(self, path):
		"""Returns the node for a path given relative to the WatchFolders path."""
		
		# If we have no root node then there are no other nodes so return None.
		if len( FileNode.objects.filter(parent=self.root_node) ) == 0:
			return None
		
		current_node = self.root_node
		
		# WARNING: Non portable / Linux specific.
		
		# Travel all the way down the given path node by node
		
		for p in path.split("/"):
			items = FileNode.objects.filter(parent=current_node, name=p)
			if len(items) == 1:
				current_node = items[0]
			elif len(items) == 0:
				return None
			else:
				# We got two nodes with the same name, suggests bad data in db.
				raise LookupError
		
		# If we got here then we must have the found the node, lets return it.
		return current_node
	
	
	def create_node(self, path, name):
		"""Create a node to represent a given name in a given path where the path is relative to the WatchFolder's root path"""
		
		parts = [ p for p in path.split("/") if len(p) ]
		
		if len(parts) == 0:
			# No path was given so create the node as a child of the WatchFolder's root node.
			
			created = datetime.datetime.now()
			node = FileNode.objects.create(name=name, parent=self.root_node, directory=os.path.isdir( os.path.join(self.path, path, name) ), created=created, updated=created)
			node.save()
		else:
			# We have a path so we need to traverse along it, creating any non-existant nodes as we go
			
			current_path = ""
			for p in parts:
				current_path = os.path.join(current_path, p)
				parent = self.get_node(current_path)
				if parent == None:
					self.create_node(current_path, p)
			
			created = datetime.datetime.now()
			node = FileNode.objects.create(name=name, parent=parent, directory=os.path.isdir( os.path.join(self.path, path, name) ), created=created, updated=created)
			node.save()
		
		return node
	
	
	def __unicode__(self):
		return self.path


class SyncLog(models.Model):
	"""Log of any update to the filesystem representation database"""
	
	created = models.DateTimeField()
	log = models.TextField()
	nodes_added = models.ManyToManyField(FileNode, related_name="added")
	nodes_modified = models.ManyToManyField(FileNode, related_name="modified")
	nodes_removed = models.ManyToManyField(FileNode, related_name="removed")
	
	
	def __unicode__(self):
		return u"%s - %s" % ( str(self.created), self.log )
	
	
	class Meta:
		ordering = ['created']


class ExclusionTime(models.Model):
	"""Define time at which a package cannot be downloaded"""
	
	# Message to explain to the user why they cannot download at this time
	message = models.TextField(blank=True, null=True)
	start = models.TimeField()
	end = models.TimeField()


class Package(models.Model):
	"""A package that can be created and then later downloaded by a user that is not authenticate on the system"""
	
	# The node representing the file / folder from which the package was created
	node = models.ForeignKey(FileNode)
	
	# Unique identifier for the package, used for temporary file and user URL.
	uuid = models.CharField(max_length=255)
	
	# Number of downloads of the package that can take place before it becomes invalid
	downloads_permitted = models.IntegerField()
	# Count of the number of downloads used
	downloads_used = models.IntegerField()
	
	# Time & Date from which the package can be downloaded
	valid_from = models.DateTimeField(blank=True, null=True)
	
	# Time & Date up until the package can be downloaded
	valid_until = models.DateTimeField(blank=True, null=True)
	
	# Times of day at which the package cannot be downloaded
	excusion_times = models.ManyToManyField(ExclusionTime, related_name="exclusion_times")
	
	# Message to display to user when downloading the package
	message = models.TextField(blank=True, null=True)
	








