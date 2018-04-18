# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.dateparse import parse_date
import re
import bcrypt
import datetime


class UserManager(models.Manager):
    def register_validator(self, POSTdata):
        #My validation steps here
        reg_errors = []
        if len(POSTdata['name']) is 0:
            reg_errors.append('Name can\'t be empty')
        elif len(POSTdata['name']) < 3:
            reg_errors.append('Name should be 3 characters at least')

        if len(POSTdata['username']) is 0:
            reg_errors.append('Username can\'t be empty')
        elif len(POSTdata['username']) < 3:
            reg_errors.append('Username should be 3 characters at least')

        if len(POSTdata['password']) is 0:
            reg_errors.append('Please provide a password')
        elif len(POSTdata['password']) < 8:
            reg_errors.append('Password must be at least 8 characters')
        elif len(POSTdata['pwd_conf']) is 0:
            reg_errors.append('Please confirm your password')
        elif POSTdata['password'] != POSTdata['pwd_conf']:
            reg_errors.append('Password confirmation not matching')

        if len(reg_errors) > 0:
            #Validation failed
            return (False, reg_errors)
        else:
            #Validation succeed
            search = self.filter(username=POSTdata['username'])
            if len(search) > 0:
                # Username already exists
                reg_errors.append('Username entered is not available.')
                return (False, reg_errors)
            else:
                # Username does not exists
                reg_user = self.create(
                    name = POSTdata['name'],
                    username = POSTdata['username'],
                    password = bcrypt.hashpw(POSTdata['password'].encode(), bcrypt.gensalt())
                )
                return (True, reg_user)
        
    def login_validator(self, POSTdata):
        log_errors = []
        if len(POSTdata['username']) is 0:
            log_errors.append('Username is required!')

        if len(POSTdata['password']) is 0:
            log_errors.append('Password is required')

        if len(log_errors) > 0:
            return (False, log_errors)
        else: 
            # find user by email
            search = self.filter(username=POSTdata['username'])
            if len(search) > 0:
                # Username found!
                user = search[0]
                if bcrypt.checkpw(POSTdata['password'].encode(), user.password.encode()):
                    # correct password
                    return (True, user)
                else:
                    # incorrect password
                    log_errors.append('Invalid Username or Password')
                    return (False, log_errors)
            else:
                # User not found/registered
                log_errors.append('Invalid Username or Password')

# Remember to add the objects = ThisManager() into the respective class
class PlanManager(models.Manager):
    def newplan_validator(self, POSTdata, logged_id):
        plan_errors = []
        start = parse_date(POSTdata['start_date'])
        end = parse_date(POSTdata['end_date'])

        if len(POSTdata['destination']) is 0:
            plan_errors.append('Please enter a Destination')
        elif len(POSTdata['destination']) < 3:
            plan_errors.append('Destination should be at least 3 characters.')
        
        if len(POSTdata['details']) is 0:
            plan_errors.append('Please enter some details of your Plan')

        if start is None:
            plan_errors.append('Please enter a Departurte Date')
        elif end is None:
            plan_errors.append('Please enter a Return Date')
        
        if len(plan_errors) > 0:
            return (False, plan_errors)
        else:
            if start < datetime.date.today() or end < datetime.date.today():
                plan_errors.append('Dates cannot be set in the past.')
                return (False, plan_errors)
            elif end < start:
                    plan_errors.append('Return Date cannot be set before Departure Date.')
                    return (False, plan_errors)
                    
            new_plan = self.create(
                destination = POSTdata['destination'],
                details = POSTdata['details'],
                start_date = POSTdata['start_date'],
                end_date = POSTdata['end_date'],
                created_by = User.objects.get(id = logged_id),
            )
            User.objects.get(id=logged_id).joined_plans.add(new_plan)
            return (True, new_plan)

    def join_plan(self, who_id, plan_id):
        User.objects.get(id = who_id).joined_plans.add(self.get(id=plan_id))
        return self

class User(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    #Time stamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #Validation functionality extend
    objects = UserManager()

    def __repr__(self):
        return "[{}]: {}".format(self.id, self.username)

class Plan(models.Model):
    destination = models.CharField(max_length=255)
    details = models.TextField(null=True)
    start_date = models.DateTimeField(auto_now_add=False)
    end_date = models.DateTimeField(auto_now_add=False)
    created_by = models.ForeignKey(User, related_name="created_plans")
    joined_users = models.ManyToManyField(User, related_name="joined_plans")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PlanManager()

    def __repr__(self):
        return "[{}]: to: {} by:{}".format(self.id, self.destination, self.created_by)