from django.shortcuts import render, redirect
from .forms import DeviceForm, CheckoutForm, Checkinform, RegisterUser
from .models import checkedout, History, Device
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
import datetime
import bleach
from inventoryapp.checks import maccheck, jscheck
from django.contrib.auth.models import Group, User


#session logic
def session(request):
    #grabs number of visits and adds one
    visitnumber = request.session.get('num_visits', 0) + 1
    #visit number
    request.session['num_visits'] = visitnumber
    #Checks number of visits
    if visitnumber > 5:
        del(request.sessions['num_visits'])
    return HttpResponseRedirect("/")

#add new devices to the DB
def add(request):
    title='Add New Device'
    #grabs form used for web page
    form = DeviceForm(request.POST or None)
    #Grab the mac value that was sent in
    newdevice = request.POST.get('mac_address')
    #initialize message
    messages.info(request, '')
    #values sent to the html
    context = {
        "title": title,
        "form": form,
        }
    #verifies if form is valid
    if form.is_valid():
        check = maccheck.is_valid_mac(newdevice)
        if "Sorry" in check:
            messages.warning(request, check)
            return HttpResponseRedirect("/add")
        #checks if any blacklisted characters are present
        returnval = jscheck.checkforjs(newdevice)
        if 'Sorry' in returnval:
            #present message
            messages.info(request, returnval)
            #redirect to page for retry
            return HttpResponseRedirect("/add")
        #if no illegal chars are found it saves the data
        form.save()
        #craft and present success message
        messages.success(request, 'Your device has been added!')
        #redirect to page
        return HttpResponseRedirect("/add")

    return render(request, "add.html",context)

#checkout logic
def checkout(request):
    title='Check out a Device'
    #grabs checkout form
    form = CheckoutForm(request.POST or None)
    #grabs input from user
    query = request.POST.get('device')
    #sets message
    messages.info(request, '')
    #grabs all mac addresses from the Devices model
    macs = Device.objects.values_list('mac_address', flat=True)
    #data sent to the html page
    context = {
        "title": title,
        "form": form,
        "macs":macs,
        }
        #verifies if form is valid
    if form.is_valid():
        #escapes html
        q = bleach.clean(query)
        #sanitize input from user
        ID_number = bleach.clean(request.POST.get('ID_number'))
        username = bleach.clean(request.POST.get('username'))
        location = bleach.clean(request.POST.get('location'))
        #grabs all variables needed for model
        varlist = [ID_number, username, location, q]
        check = maccheck.is_valid_mac(q)
        if "Sorry" in check:
            messages.warning(request, check)
            return HttpResponseRedirect("/checkout")
        # loops through variables to for JS illegal chars
        for val in varlist:
            #checks if any blacklisted characters are present
            returnval = jscheck.checkforjs(val)
            if 'Sorry' in returnval:
                #present message
                messages.info(request, returnval)
                #redirect to checkout page for retry
                return HttpResponseRedirect("/checkout")
        try:
            #search for device to see if it is present
            device = Device.objects.get(mac_address=q)
        except:
            #creaft error message if device is not present
            msg = "Error: " + q + " Does not exist."
            #present error messsage
            messages.info(request, msg)
            #redirect for retry
            return HttpResponseRedirect("/checkout")
        #Craft new device object
        newDevice = checkedout(
                    device = device,
                    ID_number = ID_number,
                    username = username,
                    location = location,
                    checkedoudate = datetime.datetime.now(),
                    )

        #cleans fields if needed
        try: 
            newDevice.clean_fields()
            #check if device is present in checked out DB
            devicecheck = checkedout.objects.filter(device_id=q)
            devicecheck = devicecheck.values()[0]
            #craft error message if device is not present
            msg = "Error: " + q + " is already checked out."
            #present error messsage
            messages.info(request, msg)
            #redirect for retry
            return HttpResponseRedirect("/checkout")
        except:
            print('test')
            #pass
            #if no errors save the object
            newDevice.save()
            #success message
            messages.success(request, 'Your device has been checked out successfully!')
            #redirect to checkoutpage
            return HttpResponseRedirect("/checkout")
    return render(request, "checkout.html",context)

def checkin(request):
    title='Check in a Device'
    #grabs form
    form = Checkinform(request.POST or None)
    #gets input data
    query = request.GET.get('search')
    #initializes message
    messages.info(request, '')
    #grabs all macs currently checked out
    macs = checkedout.objects.values_list('device', flat=True)
    #data sent to html page
    context = {
        "title": title,
        "form": form,
        "macs":macs,
        }
    #if the input is not empty proceed
    if query != None and query != '':
        #clean input
        q = bleach.clean(query)
        mac = q
        #checks for illegal chars
        check = maccheck.is_valid_mac(mac)
        if "Sorry" in check:
            messages.warning(request, check)
            return HttpResponseRedirect("/checkin")
        #checks if any blacklisted characters are present
        returnval = jscheck.checkforjs(mac)
        if 'Sorry' in returnval:
            #present message
            messages.info(request, returnval)
            return HttpResponseRedirect("/checkin")
        try:
            #search for the device that is being checked in
            device = checkedout.objects.filter(device_id=mac)
            datadict = device.values()[0]
            #grabs values from query and creates an entry in the history model
            historyentry = History(mac_address = datadict['device_id'], ID_number = datadict['ID_number'], username = datadict['username'], location = datadict['location'], checkedoutdaterecord = datadict['checkedoudate'])
            #saves to the history model
            historyentry.save()
            #deletes the device in the checked out table
            device.delete()
            #success message
            messages.success(request, 'Success: Your device has been checked in.')
            #redirect for new check in
            return HttpResponseRedirect("/checkin")
        except:
            #error message if device does not exist
            msg = "Error: " + q + " Does not exist."
            messages.info(request, msg)
            return HttpResponseRedirect("/checkin")

    return render(request, "checkin.html",context)

#home page logic
def home(request):
    #Grabs count of mobile, laptops, and desktops to present in a dynamic graph
    mobilecount = Device.objects.filter(device_type="Mobile").count()
    laptopcount = Device.objects.filter(device_type="Laptop").count()
    desktopcount = Device.objects.filter(device_type="Desktop").count()
    title = 'Welcome to DeviceTracker'
    #data sent to the home page
    context = {
        "title": title,
        "mobile":mobilecount,
        "desktop":desktopcount,
        "laptop":laptopcount,
        }
    return render(request, "home.html",context)

#new user registration (not admin)
def register(request):
    #grabs username input
    username = request.POST.get('username')
    #grabs groups
    superuser = Group.objects.get(name='Superusers') 
    standarduser = Group.objects.get(name='StandardUsers') 
    #If method is POST proceed
    if request.method == "POST":
        #grabbing form
        form = RegisterUser(request.POST)
        #validating form
        if form.is_valid():
            #save new user
	        form.save()
        #grabs superuser status of new user
        is_superuser = request.POST.get('is_superuser')
        #grabs staff status of new user
        is_staff = request.POST.get('is_staff')
        #grabs DB ID of user
        id = User.objects.only('id').get(username=username).id
        #if staff or superuser then add the user to the useruser group
        if is_staff == 'on' or is_superuser == 'on':
            superuser.user_set.add(id)
        else:
            #if there are not special permissions add to standard group
            standarduser.user_set.add(id)
        #go home
        return redirect("/")
    else:
        #display form if GET
	    form = RegisterUser()
    return render(request, "register.html", {"form":form})