from django import forms

from django.contrib.auth.models import User
from .models import Profile


# class LoginForm(forms.Form):
#     # username = forms.CharField()
#     username = forms.CharField(widget=forms.TextInput(
#         attrs={'class': 'form-control'}
#     ))
#     password = forms.CharField(widget=forms.PasswordInput(
#         attrs={'class': 'form-control'}
#     ))


# Registration form of new user
class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    # Check passwords are the same
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match')
        return cd['password2']


# Form for editing logedin user data User
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# Form for editing logedin user data Profile
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birht', 'photo']
