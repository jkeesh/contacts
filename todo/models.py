from django.db import models

from django.contrib.auth.models import User

import datetime
from datetime import timedelta

class UserProfile(models.Model):
    """
    Extension of the basic Django User
    """
    user            =       models.OneToOneField(User)
    bio             =       models.CharField(max_length=255, blank=True, null=True, default="")

    def __unicode__(self):
        return "%s" % self.user


class Contact(models.Model):
	"""
	A contact is someone you want to get back in touch with
	"""
	user 			= 		models.ForeignKey(User)				# Who does this contact belong to?
	name			=		models.CharField(max_length=100)	# The contacts name

	# Next time to check in, default is one week from today
	date			=		models.DateField(default=datetime.date.today() + timedelta(weeks=1))					


class Note(models.Model):
	"""
	This represents a note about a contact
	"""
	contact 		=		models.ForeignKey(Contact, null=True)			# Who is this note about
	text			=		models.TextField()					# Note about the contact
	timestamp		= 		models.DateTimeField(auto_now_add=True)

