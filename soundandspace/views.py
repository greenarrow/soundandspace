from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
import mimetypes, os

from soundandspace import models, archive



def get_generic_values(request):
	"""Returns dicionary of values used in all views"""
	
	# TODO: Useragent detection to switch to mobile browser mode
	return {"mobile":True}


def index(request):
	"""The home screen"""
	folders = models.WatchFolder.objects.filter()
	
	dictionary = {"folders":folders}
	dictionary.update( get_generic_values(request) )
	
	return render_to_response( "soundandspace/index.html", dictionary, context_instance=RequestContext(request) )


def view_node(request, node_id):
	"""Display a given node in the db filesystem representation"""
	node = models.FileNode.objects.get(id=node_id)
	
	dictionary = {"node":node}
	dictionary.update( get_generic_values(request) )
	
	return render_to_response( "soundandspace/view_node.html", dictionary, context_instance=RequestContext(request) )


def direct_download(self, node_id):
	"""Returns data to download for a given node. Creates an archive if the node is a directory"""
	
	node = models.FileNode.objects.get(id=node_id)
	
	if node.directory and not node.is_empty():
		# We have directory with files in so build an archive
		
		zipfile = archive.ZipFile(node)
		
		wrapper = FileWrapper( file(zipfile.filename) )
		
		response = HttpResponse(wrapper, mimetype='application/zip')
		response['Content-Disposition'] = 'attachment; filename="%s.zip"' % node.name
		response['Content-Length'] = os.path.getsize(zipfile.filename)
		
		return response

	elif node.directory:
		# We have an empty directory, we don't want that, that is rubbish
		# TODO: Send the user something a bit more usefull
		return HttpResponse("error: directory is empty")
	
	else:
		# The node is a file so just send it to the user as is.
		filename = node.get_absolute_path()
		wrapper = FileWrapper( file(filename) )
		
		response = HttpResponse( wrapper, mimetype=mimetypes.guess_type(filename) )
		response['Content-Disposition'] = 'attachment; filename="%s"' % node.name
		response['Content-Length'] = os.path.getsize(filename)
		
		return response
	



