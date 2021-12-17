from django.db import models
from .validators import is_valid_mac

# Create your models here.
class Device(models.Model):
    #choices available for device type
    choices = (
        ('Mobile', 'IOS'),
        ('Laptop', 'Laptop'),
        ('Desktop', 'Desktop'),
    )
    device_type = models.CharField(max_length=25, choices=choices, default="Choose a type")
    #PK
    mac_address = models.CharField(max_length=25,primary_key=True)
    available = 1
    checkedout = 2
    statuschoices = (
        (available, 'Available'),
        (checkedout, 'Checked Out'),
    )
    #status of device This is automatically set when a device is checking in or out
    status = models.PositiveIntegerField(choices=statuschoices, default=available)
    def __unicode__(self):
        return self.mac_address

class checkedout(models.Model):
    #one to one field because devices can only be checked out once. 
    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        primary_key=True,
        )
    ID_number = models.CharField(max_length=25)
    username = models.CharField(max_length=25)
    location = models.CharField(max_length=25)
    #auto time stamp of when the device is checked out
    checkedoudate = models.DateTimeField(auto_now_add=True, editable=False)

#check out history, this is only manipulated by the logic. When a device is checked in an entry is made in this table with the data
class History(models.Model):
    mac_address= models.CharField(max_length=25)
    ID_number = models.CharField(max_length=25)
    username = models.CharField(max_length=25)
    location = models.CharField(max_length=25)
    checkedoutdaterecord = models.DateTimeField()
    checkedindate = models.DateTimeField(auto_now_add=True, editable=False)