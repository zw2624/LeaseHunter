from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .forms import UserForm, ProfileForm, HouseForm, CommentForm
from .models import House

from geopy.geocoders import Nominatim

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_required
@transaction.atomic
def update_profile(request):
    '''
    update profile in database if the user click 'submit'
    '''
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    my_favorite = request.user.profile.favorites.all()
    my_house = House.objects.filter(created_by=request.user).all()
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'my_favorite': my_favorite,
        'my_house': my_house
    })

@login_required
def add_house(request):
    house_form = HouseForm()
    return render(request, 'add_house.html', {'house_form':house_form})

@login_required
def save_house(request):
    if request.method == 'POST':
        house_form = HouseForm(request.POST)
        if house_form.is_valid():
            house = house_form.save(commit=False)
            house.created_by = request.user
            geolocator = Nominatim(user_agent="Lease Hunter")
            location = geolocator.geocode(house.address + ' ' + house.city)
            house.lat = location.latitude
            house.lon = location.longitude
            house.save()
            return redirect('profile')
        else:
            messages.error(request, 'Error when adding house.')
    return redirect('profile')

@login_required
def delete(request):
    ID = request.GET.get('houseID')
    House.objects.get(id = ID).delete()
    messages.info(request, 'House deleted')
    return redirect('profile')

@login_required
@transaction.atomic
def change(request):
    ID = request.GET.get('houseID')
    house = House.objects.get(id=ID)
    if request.method == 'POST':
        house_form = HouseForm(request.POST, instance=house)
        if house_form.is_valid():
            house_form.save()
            messages.success(request, 'Your House was successfully updated!')
            return redirect('explore')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        house_form = HouseForm(instance=house)
    return render(request, "change.html", {'house_form':house_form})

@login_required
def add_comment(request):
    comment_form = CommentForm()
    ID = request.POST.get('houseID')
    return render(request, 'add_comment.html', {'id':ID, 'comment_form':comment_form})

@login_required
def save_comment(request):
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        ID = request.POST.get('houseID')
        if comment_form.is_valid():
            commet = comment_form.save(commit=False)
            commet.created_by = request.user
            commet.save()
            house = House.objects.get(id=ID)
            house.comments.add(commet)
            house.save()
            isCreator = house.created_by == request.user
            like = request.user.profile.favorites.filter(id=ID).exists()
            return render(request, 'single_house.html',{'house':house, 'is_creator':isCreator, 'like':like})
        else:
            messages.error(request, 'Error when adding house.')
    return redirect('profile')

@login_required
def like(request):
    ID = request.POST.get('id')
    house = House.objects.get(id=ID)
    request.user.profile.favorites.add(house)
    isCreator = house.created_by == request.user
    return render(request, 'single_house.html',{'house':house, 'is_creator':isCreator, 'like':True})

@login_required
def unlike(request):
    ID = request.POST.get('id')
    house = House.objects.get(id=ID)
    request.user.profile.favorites.add(house)
    isCreator = house.created_by == request.user
    return render(request, 'single_house.html',{'house':house, 'is_creator':isCreator, 'like':False})


class SignUp(generic.CreateView):
    '''
    Adapt 'lazy login' of Django.
    '''
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'