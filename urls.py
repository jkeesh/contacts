from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	(r'^$', 'todo.views.index'),

    ## User Auth
	(r'^register$', 'todo.views.register'),
	(r'^login/?$', "todo.views.login"),
    (r'^logout/?$', "todo.views.logout"),

    ## Contact
    (r'^add/?$', 'todo.views.add_contact'),
    (r'^contact/(?P<c_id>[\d]+)/$', 'todo.views.contact'),
    (r'^add_note/?$', 'todo.views.add_note'),
    (r'^change_date/?$', 'todo.views.change_date'),

    (r'^filter/?$', 'todo.views.filter'),
    (r'^search/?$', 'todo.views.search'),

    (r'^admin/', include(admin.site.urls)),
)
