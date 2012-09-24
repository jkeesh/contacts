from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect


from contacts.todo.forms import RegistrationForm

from django.contrib.auth.models import User
from contacts.todo.models import UserProfile
from contacts.todo.models import Contact
from contacts.todo.models import Note

from django.utils import simplejson

import datetime


def json_response(obj):
    """
    Helper method to turn a python object into json format and return
    an HttpResponse object.
    """
    return HttpResponse(simplejson.dumps(obj),
                        mimetype="application/x-javascript")


################################################################
#
#   Contacts
#
################################################################
def add_contact(request):
    name = request.POST['name']

    name = name.strip()

    # Can't be empty
    if len(name) == 0:
        return redirect('/')

    # Can't already exist
    exists = Contact.objects.filter(name=name, user=request.user)
    if len(exists) > 0:
        return redirect('/contact/%d' % exists[0].pk)

    contact = Contact(name=name, user=request.user)
    contact.save()

    return redirect('/contact/%d' % contact.pk)


def contact(request, c_id):
    c = Contact.objects.get(pk=c_id)
    if c.user != request.user:
        # Not their contact
        return redirect('/')

    return render_to_response("contact.html", {
        "contact": c,
        "notes": c.note_set.all().order_by('-timestamp'),
        "today": datetime.date.today(),
    },
        context_instance=RequestContext(request)
    )


def add_note(request):
    note = request.POST['note']
    c_id = request.POST['c_id']

    note = note.strip()
    if len(note) == 0:
        return redirect('/contact/%s' % c_id)

    contact = Contact.objects.get(pk=c_id)
    note = Note(text=note, contact=contact)
    note.save()

    return redirect('/contact/%s' % c_id)


def change_date(request):

    date = request.POST['date']
    c_id = request.POST['c_id']

    contact = Contact.objects.get(pk=c_id)

    print date

    new_date = datetime.datetime.strptime(date, "%m/%d/%y")
    contact.date = new_date
    contact.save()

    return json_response({
        'status': 'ok'
    })


def contact_done(request):
    c_id = request.POST['c_id']
    contact = Contact.objects.get(pk=c_id)

    contact.date = None
    contact.save()

    return json_response({
        'status': 'ok'
    })

################################################################
#
#   Filter and Search
#
################################################################


def search(request):
    query = request.GET['name']
    contacts = Contact.objects.filter(
        user=request.user, name__icontains=query).order_by('date')

    return render_to_response("home.html", {
        "contacts": contacts,
        "filter": 'search',
        "today": datetime.date.today()
    },
        context_instance=RequestContext(request)
    )


def filter(request):

    contacts = Contact.objects.filter(
        user=request.user).order_by('date').exclude(date=None)

    if 'filter' in request.GET:
        filter_type = request.GET['filter']

        delta = None

        if filter_type == "day":
            delta = datetime.timedelta(hours=1)
        elif filter_type == "week":
            delta = datetime.timedelta(weeks=1)
        elif filter_type == "twoweeks":
            delta = datetime.timedelta(weeks=2)
        elif filter_type == "month":
            delta = datetime.timedelta(weeks=4)
        elif filter_type == "twomonths":
            delta = datetime.timedelta(weeks=8)
        else:
            filter_type = "all"

        if delta:
            limit = datetime.date.today() + delta
            contacts = contacts.filter(date__lte=limit)

    return render_to_response("home.html", {
        "contacts": contacts,
        "filter": filter_type,
        "today": datetime.date.today(),
        "done_contacts": Contact.objects.filter(date=None),
    },
        context_instance=RequestContext(request)
    )


################################################################
#
#   Home Page, User Authentication
#
################################################################

def index(request):
    # If not logged in, then go to register page
    if not request.user.is_authenticated():
        return register(request)

    contacts = Contact.objects.filter(
        user=request.user).order_by('date').exclude(date=None)

    # I want the home page to be todays contacts
    delta = datetime.timedelta(hours=1)
    limit = datetime.date.today() + delta
    contacts = contacts.filter(date__lte=limit)

    return render_to_response("home.html", {
        "contacts": contacts,
        "filter": "day",
        "today": datetime.date.today()
    },
        context_instance=RequestContext(request)
    )


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            user = User.objects.create_user(email,  # email is username
                                            email,  # email
                                            password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            up = UserProfile(user=user)
            up.save()

            #request.session['next'] = '/'

            return authenticate(request, email, password)
    else:
        form = RegistrationForm()

    return render_to_response("login.html", {
        'form': form,
    },
        context_instance=RequestContext(request)
    )


def authenticate(request, email, password):
    user = auth.authenticate(username=email, password=password)
    if user is not None:
        if not user.is_active:
            auth.logout(request)
            return redirect('/')

        auth.login(request, user)

        if 'next' in request.session:
            next = request.session['next']
            del request.session['next']
            return redirect(next)

        return redirect('/')
    else:
        form = RegistrationForm()
        return render_to_response("login.html", {
            'login_error': True,  # indicates username / pword did not match
            'form': form,
        },
            context_instance=RequestContext(request)
        )


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


@csrf_protect
def login(request):
    if request.method == "POST":
        return authenticate(request, request.POST['email'],
                            request.POST['password'])
    return redirect('/')
