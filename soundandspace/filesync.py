from soundandspace import models
import os, datetime


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
	for folder in models.WatchFolder.objects.filter(watch=True):
		
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








