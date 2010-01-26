from django.db import models


class FileNode(models.Model):
	name = models.CharField(max_length=255)
	parent = models.ForeignKey("self", blank=True, null=True)
	
	created = models.DateTimeField()
	updated = models.DateTimeField()
	
	def __unicode__(self):
		return str(self.id)
	
	#class Meta:
	#	ordering = ('-node_type', 'name')


class WatchFolder(models.Model):
	path = models.CharField(max_length=1000)
	watch = models.BooleanField()
	root_node = models.ForeignKey(FileNode, blank=True, null=True)
	
	def __unicode__(self):
		return self.path


class SyncLog(models.Model):
	created = models.DateTimeField()
	log = models.TextField()
	nodes_added = models.ManyToManyField(FileNode, related_name="added")
	nodes_modified = models.ManyToManyField(FileNode, related_name="modified")

