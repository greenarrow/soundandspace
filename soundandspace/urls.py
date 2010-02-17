from django.conf.urls.defaults import *
import soundandspace.views

urlpatterns = patterns('',
	(r'^$', soundandspace.views.index),
	
	(r'^node/(\d+)$', soundandspace.views.view_node),
	(r'^node/(\d+)/download$', soundandspace.views.direct_download),

)
