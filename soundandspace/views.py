from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.servers.basehttp import FileWrapper
from django.conf import settings

from soundandspace import models, archive

import mimetypes, os


def index(request):
	folders = models.WatchFolder.objects.filter()

	return render_to_response( "soundandspace/index.html", {"folders":folders}, context_instance=RequestContext(request) )


def view_node(request, node_id):
	node = models.FileNode.objects.get(id=node_id)
	return render_to_response( "soundandspace/view_node.html", {"node":node, "mobile":True}, context_instance=RequestContext(request) )


def direct_download(self, node_id):
	node = models.FileNode.objects.get(id=node_id)
	
	if node.directory and not node.is_empty():
		# Build and archive
		
		zipfile = archive.ZipFile(node)
		
		wrapper = FileWrapper( file(zipfile.filename) )
		
		response = HttpResponse(wrapper, mimetype='application/zip')
		response['Content-Disposition'] = 'attachment; filename="%s.zip"' % node.name
		response['Content-Length'] = os.path.getsize(zipfile.filename)
		
		return response

	elif node.directory:
		# Empty directory
		return HttpResponse("empty directory")
	
	else:
		# Just send the file as is
		filename = node.get_absolute_path()
		wrapper = FileWrapper( file(filename) )
		
		response = HttpResponse( wrapper, mimetype=mimetypes.guess_type(filename) )
		response['Content-Disposition'] = 'attachment; filename="%s"' % node.name
		response['Content-Length'] = os.path.getsize(filename)
		
		return response
	



