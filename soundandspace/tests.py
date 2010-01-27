import unittest, shutil, os
from soundandspace import models, filesync

def print_node_tree(node):
	child_nodes = models.FileNode.objects.filter(parent=node)
	print "...node: ", node, child_nodes
	for cn in child_nodes:
		print_node_tree(cn)

class WatchFolderCase(unittest.TestCase):
	def setUp(self):
		
		self.path = os.path.join( os.getcwd(), "temp-test-data" )
		
		if os.path.isdir(self.path):
			shutil.rmtree(self.path)
		
		os.mkdir(self.path)
		os.mkdir( os.path.join(self.path, "test1") )
		os.mkdir( os.path.join(self.path, "test2") )
		os.mkdir( os.path.join(self.path, "test3") )
		open( os.path.join(self.path, "file1.txt"), "w").write("ok")
		open( os.path.join(self.path, "test1", "file2.txt"), "w").write("ok")
		os.mkdir( os.path.join(self.path, "test1", "test4") )
		
		watch = models.WatchFolder.objects.create(name="test folder", path=self.path, watch=True, root_node=None)
		watch.save()
	
	def tearDown(self):
		shutil.rmtree(self.path)
		#pass
	

	def testFolderScan(self):
		filesync.scan_folders()
		watch = models.WatchFolder.objects.filter(name="test folder")[0]
		print "Tree:"
		print_node_tree(watch.root_node)
		
		root_child_nodes = models.FileNode.objects.filter(parent=watch.root_node)
		print root_child_nodes
		self.assertEquals( len(root_child_nodes), 4 )
		names = [ node.name for node in root_child_nodes ]
		names.sort()
		self.assertEquals( names, ['file1.txt', 'test1', 'test2', 'test3'] )
		
		self.assertNotEqual( watch.get_node("test1"), None )
		self.assertNotEqual( watch.get_node("test2"), None )
		self.assertNotEqual( watch.get_node("test3"), None )
		self.assertNotEqual( watch.get_node("file1.txt"), None )
		self.assertNotEqual( watch.get_node("test1/file2.txt"), None )
		self.assertNotEqual( watch.get_node("test1/text4"), None )
		
		#filesync.scan_folders()
		
		#print "Tree:"
		#print_node_tree(watch.root_node)
		
		self.assertEquals(True, True)

