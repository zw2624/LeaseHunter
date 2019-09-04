from django import forms
from django.contrib.auth.models import User
from users.models import Profile, House, Comment

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('birth_date', 'website', 'address')

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ('address', 'city', 'state', 'postal', 'name', 'beds', 'baths', 'rent', 'deposit','unit', 'lease_length', 'available', 'desciption')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
