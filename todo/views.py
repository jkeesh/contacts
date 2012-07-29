from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect


from todo.forms import RegistrationForm

from django.contrib.auth.models import User
from todo.models import UserProfile
from todo.models import Contact
from todo.models import Note

from django.utils import simplejson

import datetime

def json_response(obj):
    """
    Helper method to turn a python object into json format and return an HttpResponse object.
    """
    return HttpResponse(simplejson.dumps(obj), mimetype="application/x-javascript")


################################################################
#
#   Contacts
#
################################################################
def add_contact(request):
    name = request.POST['name']

    contact = Contact(name=name, user=request.user)
    contact.save()

    return redirect('/')

def contact(request, c_id):
    c = Contact.objects.get(pk=c_id)
    if c.user != request.user:
        # Not their contact
        return redirect('/')

    return render_to_response("contact.html", {
            "contact": c,
            "notes": c.note_set.all().order_by('-timestamp')
        },
        context_instance = RequestContext(request)
    )

def add_note(request):
    note = request.POST['note']
    c_id = request.POST['c_id']

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


def filter(request):

    contacts = Contact.objects.filter(user=request.user).order_by('date')

    if 'filter' in request.GET:
        filter_type = request.GET['filter']

        delta = None

        if filter_type == "day":
            delta = datetime.timedelta(days=1)
        elif filter_type == "week":
            delta = datetime.timedelta(weeks=1)
        elif filter_type == "twoweeks":
            delta = datetime.timedelta(weeks=2)
        elif filter_type == "month":
            delta = datetime.timedelta(weeks=4)
        elif filter_type == "twomonths":
            delta = datetime.timedelta(weeks=8)

        print datetime.date.today()

        if delta:
            limit = datetime.date.today() + delta
            print limit

            contacts = contacts.filter(date__lte=limit)

    return render_to_response("home.html", {
            "contacts": contacts
        },
        context_instance = RequestContext(request)
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

    contacts = Contact.objects.filter(user=request.user).order_by('date')

    return render_to_response("home.html", {
			"contacts": contacts
        },
        context_instance = RequestContext(request)
    )

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            user = User.objects.create_user(email, #email is username
                                            email, #email
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
        context_instance = RequestContext(request)
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
                'login_error': True, # indicates username / pword did not match
                'form': form,
            },
            context_instance = RequestContext(request)
        )
        
@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')

@csrf_protect
def login(request):
    if request.method == "POST":
        return authenticate(request, request.POST['email'], request.POST['password'])
    return redirect('/')