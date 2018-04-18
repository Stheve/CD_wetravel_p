# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from .models import *   # Includes all Classes.
from django.contrib import messages # For error Messages

def index(request):
    return redirect('/travels')

def travels(request):
    # IF there is no "Logged" in session will redirect to login, else will render travels page (aka index.html) 
    if 'logged' not in request.session:
        return redirect('/logreg')
    else:
        context = {
            'logged_plans': User.objects.get(id = request.session['logged']['id']).joined_plans.all(),
            'others_plans': Plan.objects.exclude(joined_users__id=request.session['logged']['id'])
        }

        return render(request, 'travel_buddy/index.html', context)

def logreg(request):
    #Loads login and registration page.
    return render(request, 'travel_buddy/logreg.html')

def registration(request):
    validation = User.objects.register_validator(request.POST)
    if validation[0]:
        # Validated
        request.session['logged'] = {
            'id': validation[1].id,
            'name': validation[1].name,
            'username': validation[1].username
        }
    else:
        # Not valid
        for error in validation[1]:
            messages.add_message(request, messages.INFO ,error)
    
    return redirect('/travels')

def login(request):
    validation = User.objects.login_validator(request.POST)
    if validation[0]:
        # Validated, move on
        request.session['logged'] = {
            'id': validation[1].id,
            'name': validation[1].name,
            'username': validation[1].username
        }
    else:
        # Not valid, errors time!
        for error in validation[1]:
            messages.add_message(request, messages.INFO ,error)
        return redirect('/')

    return redirect('/travels')

def logout(request):
    del request.session['logged']
    # request.session.modified = True
    return redirect('/travels')

def add_plan(request):
    validation = Plan.objects.newplan_validator(request.POST, request.session['logged']['id'])
    if validation[0]:
        # Valid
        return redirect('/travels')
    else:
        # Invalid
        for error in validation[1]:
            messages.add_message(request, messages.INFO ,error)
        return redirect('/travels/new')

def new_plan(request):
    return render(request, 'travel_buddy/newplan.html')

def join_plan(request, plan_id):
    Plan.objects.join_plan(request.session['logged']['id'], plan_id)
    return redirect('/travels')

def view_plan(request, plan_id):
    context = {
        'destination': Plan.objects.get(id=plan_id),
        'joined_it': Plan.objects.get(id=plan_id).joined_users.all()
    }
    return render(request, 'travel_buddy/destination.html', context)