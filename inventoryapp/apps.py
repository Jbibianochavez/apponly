from django.apps import AppConfig
import sys

class InventoryappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventoryapp'
    #adds super user and standard user group at runtime
    def ready(self):
        try:
            #imports needed models
            from django.contrib.auth.models import Group
            from django.contrib.auth.models import Group, Permission
            #create groups
            Group.objects.create(name='StandardUsers')
            g2 = Group.objects.create(name='Superusers')
            #grab all permissions
            permissions = Permission.objects.all()
            #set all permissions for superuser group
            g2.permissions.add(*permissions)
        except:
            pass
