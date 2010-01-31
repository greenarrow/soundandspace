from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from soundandspace import models


def index(request):
	folders = models.WatchFolder.objects.filter()

	return render_to_response( "soundandspace/index.html", {"folders":folders}, context_instance=RequestContext(request) )


def view_node(request, node_id):
	node = models.FileNode.objects.get(id=node_id)
	return render_to_response( "soundandspace/view_node.html", {"node":node, "mobile":True}, context_instance=RequestContext(request) )
