from django.contrib import admin
from .forms import DeviceForm, CheckoutForm, Checkinformadmin
from django.urls import path, reverse
from django.shortcuts import render
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Device
from inventoryapp.checks import maccheck

# Register your models here.
from .models import Device, checkedout, History
#form for CSV file
class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()

class DeviceAdmin(admin.ModelAdmin):
    #admin page configs
    readonly_fields = ["device_type", "mac_address"]
    list_display = ["device_type", "mac_address"]
    form = DeviceForm
    list_filter = ['device_type', 'mac_address']
    search_fields = ['device_type', 'mac_address']
    #URL for CSV bulk upload page
    def get_urls(self):
        urls = super().get_urls()
        #creates new url in admin setion named csv
        new_urls = [path('csv/', self.csvupload,name='csv'), ]
        return new_urls + urls

    def csvupload(self, request):
        #when post proceed
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            #checks if this is a CSV
            if not csv_file.name.endswith('.csv'):
                #error message when non-CSV is uploaded
                messages.warning(request, 'The wrong file type was uploaded')
                #redirect for retry
                return HttpResponseRedirect(request.path_info)
            #reads CSV file
            file_data = csv_file.read().decode("utf-8")
            #string manipulation to parse data from CSV
            csv_data = file_data.split("\n")
            title1 = csv_data[0].split(',')[0]
            title2 = csv_data[0].split(',')[1].split('\\')[0]
            #accounts for carriage return 
            mac = title2.replace('\r', '')
            #verifies that the correct titles are present
            if title1 == "device_type" and mac == "mac_address":
                for x in csv_data:
                    #grabds field
                    field = x.split(",")
                    #if we are in the title row skip
                    if 'device_type' in x:
                        print("skipping title")
                        continue
                    #searches for device being uploaded
                    try:
                        device = Device.objects.get(mac_address=field[1])
                    except:
                    #sets variable to null if device is not present in the DB
                        device = ''
                    try:
                        #if device is present skip because we do not need to add it again. 
                        if device != '':
                            skipstring = "Skipped: Device " + field[1] + " is already in the db."
                            messages.warning(request, skipstring)
                            continue
                        #removes carriage return from fields
                        cleanfield0 = field[0].replace('\r', '')
                        cleanfield1 = field[1].replace('\r', '')
                        check = maccheck.is_valid_mac(cleanfield1)
                        if "Sorry" in check:
                            messages.warning(request, check)
                            continue
                        #creates new devices in the model
                        created = Device.objects.update_or_create(
                            #capitalized first letter because this is needed for the model
                            device_type = cleanfield0.capitalize(),
                            mac_address = cleanfield1.upper(),
                            )                 
                    except:
                        pass
            else:
                #error message if titles are not present or incorrect.
                messages.warning(request, 'The wrong titles were found. Please ensure you use device_type and mac_address as titles')
                #redirect
                return HttpResponseRedirect(request.path_info)
            #redirect to admin page if all goes well
            url = reverse('admin:csv')
            return HttpResponseRedirect(url)
        #CSV import form
        form = CsvImportForm()
        context = {"form": form}
        return render(request, "admin/csvupload.html", context)
admin.site.register(Device, DeviceAdmin)


class Checkout(admin.ModelAdmin):
    #admin page configs
    readonly_fields = ('checkedoudate','ID_number', 'username','location')
    list_display = ["username", "device"]
    form = CheckoutForm
    list_filter = ['username']
    search_fields = ['ID_number', 'username','location']
admin.site.register(checkedout, Checkout)

class Checkin(admin.ModelAdmin):
    #admin page configs
    readonly_fields = ('checkedoutdaterecord','checkedindate',"username","mac_address","checkedoutdaterecord","checkedindate","location","ID_number")
    list_display = ["username","mac_address","checkedoutdaterecord","checkedindate",]
    form = Checkinformadmin
    list_filter = ['username']
    search_fields = ['ID_number', 'username','location']
admin.site.register(History, Checkin)