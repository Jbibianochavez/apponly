from django import forms
from django.db import models
from django.forms import fields, CharField
from .models import Device, History, checkedout
from .validators import is_valid_mac
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

#New device form
class DeviceForm(forms.ModelForm):
    #sets validator to ensure MAC is in the correct format
    mac_address = CharField(validators=[is_valid_mac])
    class Meta:
        #fields shown in the html page
        model = Device
        fields = ['device_type',
                  'mac_address']

#check out form
class CheckoutForm(forms.ModelForm):
    class Meta:
        #fields shown in the HTML form
        model = checkedout
        fields = [
                  'ID_number',
                  'username',
                  'location']

#check in form
class Checkinform(forms.ModelForm):
    #we also must validate if the mac is in the correct format
    mac_address = CharField(validators=[is_valid_mac])
    class Meta:
        #fields show in the HTML page
        model = Device
        fields = ['mac_address']

#form for the check in data
class Checkinformadmin(forms.ModelForm):
    class Meta:
        model = History
        fields = ['mac_address', 'ID_number', 'username', 'location']

#register user form
class RegisterUser(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    is_staff = forms.BooleanField(required=False)
    is_superuser = forms.BooleanField(required=False)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name','email', 'password1', 'password2', 'is_staff', 'is_superuser']
