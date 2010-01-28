import unittest, shutil, os, datetime
from soundandspace import models, filesync

def print_node_tree(node):
	child_nodes = models.FileNode.objects.filter(parent=node)
	print "...node: ", node, child_nodes
	for cn in child_nodes:
		print_node_tree(cn)

def create_test_tree(path):
	if os.path.isdir(path):
		shutil.rmtree(path)

	os.mkdir(path)
	os.mkdir( os.path.join(path, "test1") )
	os.mkdir( os.path.join(path, "test2") )
	os.mkdir( os.path.join(path, "test3") )
	open( os.path.join(path, "file1.txt"), "w").write("ok")
	open( os.path.join(path, "test1", "file2.txt"), "w").write("ok")
	open( os.path.join(path, "test2", "file3.txt"), "w").write("ok")
	os.mkdir( os.path.join(path, "test1", "test4") )

def remove_test_tree(path):
	shutil.rmtree(path)


class FileNodeCase(unittest.TestCase):
	def setUp(self):
		self.path = os.path.join( os.getcwd(), "temp-test-data" )
		create_test_tree(self.path)
	
	def tearDown(self):
		remove_test_tree(self.path)

	def testCheckExistsFilesystem(self):
		created = datetime.datetime.now()
		node1 = models.FileNode.objects.create(name="test1", parent=None, created=created, updated=created)
		node1.save()
		
		node2 = models.FileNode.objects.create(name="testnothere", parent=None, created=created, updated=created)
		node2.save()
		
		self.assertTrue( node1.check_exists_filesystem() )
		self.assertFalse( node2.check_exists_filesystem() )
		
		
	
	def testRemoveChildTree(self):
		self.assertTrue(False)


class ReScanCase(unittest.TestCase):
	def setUp(self):
		
		self.path = os.path.join( os.getcwd(), "temp-test-data" )
		
		create_test_tree(self.path)
		
		watch = models.WatchFolder.objects.create(name="test folder", path=self.path, watch=True, root_node=None)
		watch.save()
	
	def tearDown(self):
		remove_test_tree(self.path)
	

	def testInitialScan(self):
		"""First Scan: Scan test folder from clean database and check everything is found correctly"""
		models.FileNode.objects.all().delete()
		filesync.scan_folders()
		watch = models.WatchFolder.objects.filter(name="test folder")[0]
		
		root_child_nodes = models.FileNode.objects.filter(parent=watch.root_node)
		names = [ node.name for node in root_child_nodes ]
		names.sort()
		self.assertEquals( names, ['file1.txt', 'test1', 'test2', 'test3'] )
		
		self.assertNotEqual( watch.get_node("test1"), None )
		self.assertNotEqual( watch.get_node("test2"), None )
		self.assertNotEqual( watch.get_node("test3"), None )
		self.assertNotEqual( watch.get_node("file1.txt"), None )
		self.assertNotEqual( watch.get_node("test1/file2.txt"), None )
		self.assertNotEqual( watch.get_node("test1/test4"), None )
		self.assertNotEqual( watch.get_node("test2/file3.txt"), None )
	
	
	def testSecondScanNoChange(self):
		"""Re-Scan No Change: Scan test folder, then scan again before any changes to make sure that no erroneous changes are made in the database"""
		models.FileNode.objects.all().delete()
		filesync.scan_folders()
		filesync.scan_folders()
		
		watch = models.WatchFolder.objects.filter(name="test folder")[0]
		
		root_child_nodes = models.FileNode.objects.filter(parent=watch.root_node)
		names = [ node.name for node in root_child_nodes ]
		names.sort()
		self.assertEquals( names, ['file1.txt', 'test1', 'test2', 'test3'] )
		
		self.assertNotEqual( watch.get_node("test1"), None )
		self.assertNotEqual( watch.get_node("test2"), None )
		self.assertNotEqual( watch.get_node("test3"), None )
		self.assertNotEqual( watch.get_node("file1.txt"), None )
		self.assertNotEqual( watch.get_node("test1/file2.txt"), None )
		self.assertNotEqual( watch.get_node("test1/test4"), None )
		self.assertNotEqual( watch.get_node("test2/file3.txt"), None )
	
	
	def testSecondScanAddFiles(self):
		"""Re-Scan Add Files: Scan test folder, then add more files and scan again. Make sure additions are correctly added to database"""
		models.FileNode.objects.all().delete()
		filesync.scan_folders()
		
		os.mkdir( os.path.join(self.path, "test4") )
		os.mkdir( os.path.join(self.path, "test1", "test5") )
		open( os.path.join(self.path, "test1", "test5", "file6.txt"), "w").write("ok")
		
		filesync.scan_folders()
		
		watch = models.WatchFolder.objects.filter(name="test folder")[0]
		
		root_child_nodes = models.FileNode.objects.filter(parent=watch.root_node)
		names = [ node.name for node in root_child_nodes ]
		names.sort()
		self.assertEquals( names, ['file1.txt', 'test1', 'test2', 'test3', 'test4'] )
		
		self.assertNotEqual( watch.get_node("test1"), None )
		self.assertNotEqual( watch.get_node("test2"), None )
		self.assertNotEqual( watch.get_node("test3"), None )
		self.assertNotEqual( watch.get_node("test4"), None )
		self.assertNotEqual( watch.get_node("file1.txt"), None )
		self.assertNotEqual( watch.get_node("test1/file2.txt"), None )
		self.assertNotEqual( watch.get_node("test1/test4"), None )
		self.assertNotEqual( watch.get_node("test1/test5"), None )
		self.assertNotEqual( watch.get_node("test1/test5/file6.txt"), None )
		self.assertNotEqual( watch.get_node("test2/file3.txt"), None )
	
	def testSecondScanRemoveFiles(self):
		"""Re-Scan Remove Files: Scan test folder, then remove some files and scan again. Make sure removals are correctly removed to database"""
		models.FileNode.objects.all().delete()
		filesync.scan_folders()
		
		shutil.rmtree( os.path.join(self.path, "test1") )
		os.remove( os.path.join(self.path, "file1.txt") )
		os.remove( os.path.join(self.path, "test2", "file3.txt") )
		
		filesync.scan_folders()
		
		watch = models.WatchFolder.objects.filter(name="test folder")[0]
		
		root_child_nodes = models.FileNode.objects.filter(parent=watch.root_node)
		names = [ node.name for node in root_child_nodes ]
		names.sort()
		self.assertEquals( names, ['file1.txt', 'test1', 'test2', 'test3', 'test4'] )
		
		self.assertNotEqual( watch.get_node("test1"), None )
		self.assertNotEqual( watch.get_node("test2"), None )
		self.assertNotEqual( watch.get_node("test3"), None )

		
	def testSecondScanMixedFiles(self):
		"""Re-Scan Add & Remove Files: Scan test folder, then add & remove some files and scan again. Make sure additions & removals are correctly removed to database"""
		models.FileNode.objects.all().delete()
		filesync.scan_folders()
		
		os.mkdir( os.path.join(self.path, "test4") )
		os.mkdir( os.path.join(self.path, "test1", "test5") )
		open( os.path.join(self.path, "test1", "test5", "file6.txt"), "w").write("ok")
		
		shutil.rmtree( os.path.join(self.path, "test1") )
		os.remove( os.path.join(self.path, "file1.txt") )
		os.remove( os.path.join(self.path, "test2", "file3.txt") )
		
		filesync.scan_folders()
		
		watch = models.WatchFolder.objects.filter(name="test folder")[0]
		
		root_child_nodes = models.FileNode.objects.filter(parent=watch.root_node)
		names = [ node.name for node in root_child_nodes ]
		names.sort()
		self.assertEquals( names, ['test2', 'test3', 'test4'] )
		
		self.assertNotEqual( watch.get_node("test2"), None )
		self.assertNotEqual( watch.get_node("test3"), None )
		self.assertNotEqual( watch.get_node("test4"), None )









