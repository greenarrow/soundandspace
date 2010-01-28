from soundandspace import models
import os, datetime


def check_node_tree(node):
	child_nodes = models.FileNode.objects.filter(parent=node)
	
	node.check_exists_filesystem
	
	for cn in child_nodes:
		check_node_tree(cn)


def scan_folders():
	print "Starting Scan"
	for folder in models.WatchFolder.objects.filter(watch=True):
		
		print "scanning %s - node %s" % (folder.path, folder.root_node)
		
		# Check to see if the watch folder has a root file node. If it does not then create it.		
		if folder.root_node == None:
			created = datetime.datetime.now()
			node = models.FileNode(name="", parent=None, created=created, updated=created)
			node.save()
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
					#print "..create node", relative_path, item
					folder.create_node(relative_path, item)
		
		
		# TODO Walk though nodes in db and remove any for which items no longer exist on disk
		# TODO Create sync object detailing changes
				

