from django.shortcuts import render
from concert.forms import UserForm,UserProfileForm,ConcertForm,BandForm #TestForm
from concert.models import ConcertModel,Ticket,UserProfile,Band,User
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
from django.shortcuts import redirect
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse

def index(request):
    concertList = ConcertModel.objects.order_by('-date')    
    context = {}
    context['concertList'] = concertList
    
    if request.user.is_authenticated == True:        
        try:
            profile = UserProfile.objects.get(user=request.user)
        except:
            profile = None            
            
        if profile and profile.weAreBand:
            context['weAreBand'] = True
            
        context['tickets'] = Ticket.objects.filter(user=request.user)
    return render(request,'concert/index.html',context=context)

def about(request):    
    if request.method == 'POST' and "searchStart" in request.POST:
        keyword = request.POST.get('keyWord')
        
    return render(request,'concert/about.html')

@login_required
def cancelBooking(request,concertId):
    try:
        ticket = Ticket.objects.filter(user=request.user,concertId=concertId).get()
        if ticket != None:
            concert = ConcertModel.objects.get(concertId=ticket.concertId)
    except:
        ticket = None
        concert = None
        
    context = {'ticket':ticket,'concert':concert}
    
    if request.method == 'POST':
        if 'Yes' in request.POST:            
            for ticket in Ticket.objects.filter(concertId=concertId,user=request.user):
                ticket.delete()
        return redirect(reverse('concert:index'))
        
    return render(request,'concert/cancelBooking.html',context=context)    

@login_required
def booking(request,concertId):
    context = {}
    try:        
        concert = ConcertModel.objects.get(concertId=concertId)
        context['concert'] = concert
    except:     
        context['concert'] = None
        
    if request.method == 'POST':
        if 'Yes' in request.POST:
            ticketId = getTimeToInt()
            concertId = concert.concertId
            user = request.user    
            Ticket.objects.get_or_create(ticketId=ticketId,concertId=concertId,user=user)
            return redirect('/')
        elif 'No' in request.POST:
            return redirect('/')

    return render(request,'concert/booking.html',context=context)

def concert(request,concertId):
    context = {}
    try:
        foundConcert = ConcertModel.objects.get(concertId=concertId)
        context['concert'] = foundConcert
    except:
        context['concert'] = None;
    return render(request,'concert/concert.html',context=context)

def search(request):
    found = []
    if request.method == 'POST':
        keyword = request.POST.get('searchKeyword')       
        found = ConcertModel.objects.filter(location__contains=keyword) | ConcertModel.objects.filter(concertName__contains=keyword)| ConcertModel.objects.filter(band__bandName__contains=keyword)          
                
    return render(request,'concert/searchResult.html',context={"searchResults":found})


@login_required
def myaccount(request):    
    tickets = Ticket.objects.filter(user=request.user)
    concerts = {}
    context = {}
    context['tickets'] = tickets
    context['concerts'] = concerts
    
    for ticket in tickets:
        try:
            concerts[ticket.concertId] = ConcertModel.objects.get(concertId=ticket.concertId)            
        except:
            concerts[ticket.concertId] = None
    
    return render(request,'concert/myaccount.html',context)

@login_required
def concertAdd(request):
    concertAdded = False
    context = {}
    
    if request.method == 'POST' and "concertAdd" in request.POST:        
        concert_form = ConcertForm(request.POST)
        if concert_form.is_valid():               
            foundBand = Band.objects.get(user=request.user)
            concert = concert_form.save(commit=False)
            concert.concertId = getTimeToInt();
            concert.bandId = foundBand.bandId
            concert.band = foundBand
            if 'img' in request.FILES:
                concert.img = request.FILES['img']
            concert.save()
            concertAdded = True
            
    else:
        context['concertForm'] = ConcertForm();
        
    context['concertAdded'] = concertAdded
    return render(request,'concert/concertAdd.html',context=context)
    

def register(request):    
    registered = False    
    custom_error_msg = []
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        band_form = BandForm(request.POST)
        passedError = True
        
        if request.POST.get('pw_confirm') != request.POST.get('password'):
            custom_error_msg.append('Please, check the password confirmation')
            passedError = False
        elif request.POST.get('weAreBand') and request.POST.get('bandName') =='':
            custom_error_msg.append('Please, set your band name')
            passedError = False
            
        if passedError == True and user_form.is_valid() and profile_form.is_valid() and band_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            if request.POST.get('weAreBand'):                
                band = band_form.save(commit=False)
                band.bandName = request.POST.get('bandName')
                band.bandId = getTimeToInt()
                band.user = user
                band.save()

            registered = True
            password = request.POST.get('pw_confirm')
            authenticate(username=request.user,password=password)                
            login(request,user)
    else:
        logout(request)
        band_form = BandForm()
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    return render(request,
          'concert/register.html',
          context= {'user_form':user_form,
                    'band_form':band_form,
                    'profile_form': profile_form,
                    'registered':registered,
                    'custom_error_msg':custom_error_msg})
        

def signin(request):
    error_msg = []
    if request.method == 'POST':        
        username = request.POST.get('username')
        password = request.POST.get('password')        
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect(reverse('concert:index'))
            else:
                error_msg.append('Your account is disabled.')
        else:
            error_msg.append('Invalid signing in details')    
            
    return render(request,'concert/signin.html',context={'error_msg':error_msg})

@login_required
def signout(request):
    logout(request)
    return redirect(reverse('concert:index'))  

@login_required
def deleteAccount(request):
    confirmedToDelete = False
    
    if request.method == 'POST':
        if 'Yes' in request.POST:            
            user = User.objects.filter(username=request.user.username)
            if user != None:
                user.delete()
                logout(request)
                
                confirmedToDelete = True
        else:                
            return redirect(reverse('concert:index'))
            
    
    context = {"deleteConfirmed":confirmedToDelete}
    return render(request,'concert/deleteAccount.html',context)
    
    
    
def getTimeToInt():    
    a = datetime.now()
    a = int(a.strftime('%Y%m%d%H%M%S'))
    return a



def signup(request):
    print('*********************************')
    print(request.is_ajax)
    if request.is_ajax:
        print('this is ajax')
    else:
        print('this is not ajax')
    context = {}
    return render(request,'concert/signup.html',context)
    

def validate_username(request):
    """
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'A user with this username already exists.'
        """
    data = {}
    print("validate")
    data['error_message'] = "This is error"
    return JsonResponse(data)


def email_avail(request):
    email = request.GET.get("email", None)
    
    response = {}
    response['notEmail'] = email.find('@') == -1
    response['avail'] = User.objects.filter(username=email).exists() == False

    return JsonResponse(response)
    
    
    
    
    
    
    