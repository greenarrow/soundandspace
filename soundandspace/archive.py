from django.conf import settings
from soundandspace import models
import zipfile, uuid, os

class ZipFile():
	def __init__(self, node):
		self.filename = os.path.join( settings.PACKAGE_PATH, str(uuid.uuid4() ) )
		self.archive = zipfile.ZipFile(self.filename, 'w', zipfile.ZIP_DEFLATED)
		
		
		for cn in node.get_child_nodes():
			self.add_node_tree(cn, cn)
		
		self.archive.close()
	
	def add_node_tree(self, root_node, node):
		child_nodes = models.FileNode.objects.filter(parent=node)
	
		for cn in child_nodes:
			self.add_node_tree(cn)
		
		file_path = node.get_absolute_path()
		zip_path = node.get_relative_path(target=root_node)
		
		print "fp", file_path, "zp", zip_path
		self.archive.write(file_path, zip_path)
