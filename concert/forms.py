# -*- coding: utf-8 -*-
from django import forms
from concert.models import UserProfile,ConcertModel,Band
from django.contrib.auth.models import User
import datetime

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(widget=forms.EmailInput(attrs={'id': 'email_field'}))
    class Meta:
        model = User
        fields = ('username','password','first_name','last_name')
        
class UserProfileForm(forms.ModelForm):
    pw_confirm = forms.CharField(widget=forms.PasswordInput())    
    weAreBand = forms.BooleanField(initial=False,required=False)
    termsOfService = forms.BooleanField()
    
    class Meta:
        model = UserProfile
        fields = ('pw_confirm','weAreBand','termsOfService')

class BandForm(forms.ModelForm):
    bandName = forms.CharField(required=False)
    class Meta:
        model = Band
        fields = ('bandName',)

class DateInput(forms.DateInput):
    input_type = 'date'

class ConcertForm(forms.ModelForm):
    concertName = forms.CharField()
    location = forms.CharField()
    date = forms.DateField(initial=datetime.date.today,widget=DateInput)
    class Meta:
        model = ConcertModel
        fields = ('concertName','location','date','img') 

