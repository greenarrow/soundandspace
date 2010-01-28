from django.db import models
import datetime, os


class FileNode(models.Model):
	name = models.CharField(max_length=255)
	parent = models.ForeignKey("self", blank=True, null=True)
	
	created = models.DateTimeField()
	updated = models.DateTimeField()
	
	def check_exists_filesystem(self):
		pass
		#return os.path.exists(self
		# TODO need to get full real path
		return None
	
	def remove_child_node_tree(self):
		child_nodes = models.FileNode.objects.filter(parent=self)
		for node in child_nodes:
			node.remove_child_nodes()
		child_nodes.delete()
	
	def __unicode__(self):
		return str(self.name)
	
	#class Meta:
	#	ordering = ('-node_type', 'name')


class WatchFolder(models.Model):
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
				print "error"
		
		return current_node
			


	def create_node(self, path, name, check_exists=False):
		parts = [ p for p in path.split("/") if len(p) ]
		if len(parts) == 0:
			created = datetime.datetime.now()
			node = FileNode.objects.create(name=name, parent=self.root_node, created=created, updated=created)
			node.save()
		else:
			current_path = ""
			for p in parts:
				current_path = os.path.join(current_path, p)
				parent = self.get_node(current_path)
				if parent == None:
					self.create_node(current_path, p)
			
			created = datetime.datetime.now()
			node = FileNode.objects.create(name=name, parent=parent, created=created, updated=created)
			node.save()
		
		return node
	
	def __unicode__(self):
		return self.path


class SyncLog(models.Model):
	created = models.DateTimeField()
	log = models.TextField()
	nodes_added = models.ManyToManyField(FileNode, related_name="added")
	nodes_modified = models.ManyToManyField(FileNode, related_name="modified")





