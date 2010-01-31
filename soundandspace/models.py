from django.db import models
import datetime, os



class FileNode(models.Model):
	"""Node used in database representation of filesystem. May represent file or folder"""
	
	name = models.CharField(max_length=255)
	parent = models.ForeignKey("self", blank=True, null=True)
	directory = models.BooleanField()
	
	created = models.DateTimeField()
	updated = models.DateTimeField()
	
	def get_relative_path(self, target=None):
		node = self
		path = self.name
		while node.parent != None and node != target:
			node = node.parent
			path = os.path.join(node.name, path)
		
		if target == None:
			results = WatchFolder.objects.filter(root_node=node)
			
			if len(results):
				return path
			else:
				raise LookupError
		
		elif target == node:
			return path
		else:
			raise LookupError
		
		
	
	
	def get_absolute_path(self):
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
	
	
	def check_exists_filesystem(self):
		return os.path.exists( self.get_absolute_path() )
	
	
	def remove_child_node_tree(self):
		child_nodes = FileNode.objects.filter(parent=self)
		for node in child_nodes:
			node.remove_child_node_tree()
		child_nodes.delete()
	
	def get_child_nodes(self):
		return FileNode.objects.filter(parent=self)
	
	def is_root_node(self):
		if self.parent == None:
			results = WatchFolder.objects.filter(root_node=self)
			if len(results) == 1:
				return True
		return False
	
	def is_empty(self):
		return len( self.get_child_nodes() ) == 0
	
	def get_watch_folder(self):
		if self.parent == None:
			results = WatchFolder.objects.filter(root_node=self)
			if len(results) == 1:
				return results[0]
		raise LookupError
	
	def __unicode__(self):
		return u"%s - %s" % ( str(self.id), str(self.name) )
	
	class Meta:
		ordering = ('-directory', 'name')


class WatchFolder(models.Model):
	"""A folder that soundandspace will scan and show store in the database, then watch for changes."""
	
	name = models.CharField(max_length=255)
	path = models.CharField(max_length=1000)
	watch = models.BooleanField()
	root_node = models.ForeignKey(FileNode, blank=True, null=True)
	
	def get_node(self, path):
		parts = path.split("/")
		root_child_nodes = FileNode.objects.filter(parent=self.root_node)
		
		if len(root_child_nodes) == 0:
			return None
		
		current_node = self.root_node
		
		for p in parts:
			items = FileNode.objects.filter(parent=current_node, name=p)
			if len(items) == 1:
				current_node = items[0]
			elif len(items) == 0:
				return None
			else:
				raise LookupError
		
		return current_node
	
	
	def create_node(self, path, name):
		parts = [ p for p in path.split("/") if len(p) ]
		if len(parts) == 0:
			created = datetime.datetime.now()
			node = FileNode.objects.create(name=name, parent=self.root_node, directory=os.path.isdir( os.path.join(self.path, path, name) ), created=created, updated=created)
			node.save()
		else:
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




