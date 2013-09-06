from django import forms
from captcha.fields import ReCaptchaField
from gbvp.models import *


class RegistrationForm(UserCreationForm):
    
    password1 = forms.RegexField(label=("Password"),widget=forms.PasswordInput(attrs={'placeholder': 'Enter your Password ','onkeyup': 'passwordStrength(this.value)','class':'input-xlarge'}),regex=r'^.*(?=.{6,})(?=.*[a-z]).*$')
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={'placeholder': 'ReEnter password ','class':'input-xlarge'}))
    captcha = ReCaptchaField(attrs={'theme' : 'white'})


    class Meta:
        model = UserProfile
        fields = ('user.first_name' , 'email' , 'phone_number','gender', 'date_Of_birth')
        gender_choices = (
            ('M', 'Male'),
            ('F', 'Female'),
         )
        widgets = {
            'email': forms.TextInput(attrs = {'placeholder': 'Email example@example.com','type':'email'}),
            'name' : forms.TextInput(attrs = {'placeholder': 'Full Name'}),
            'phone_number' : forms.TextInput(attrs = {'type': 'number'}),
            'gender' : forms.Select(choices=gender_choices),
            'date_Of_birth' : forms.DateInput(attrs = {'type': 'date'}),
            

        }