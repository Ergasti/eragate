from django import forms
from captcha.fields import ReCaptchaField
from vps.models import *
from django.contrib.auth.forms import UserCreationForm


class RegistrationForm(forms.ModelForm):
    

    captcha = ReCaptchaField(attrs={'theme' : 'white'})


    class Meta:
        model = UserProfile
        fields = ( 'phone_number','gender', 'date_Of_birth')
        gender_choices = (
            ('M', 'Male'),
            ('F', 'Female'),
         )
        widgets = {
            # 'email': forms.TextInput(attrs = {'placeholder': 'Email example@example.com','type':'email'}),
            # 'name' : forms.TextInput(attrs = {'placeholder': 'Full Name'}),
            'phone_number' : forms.TextInput(attrs = {'placeholder': 'Mobile ','type': 'number','class':'form-control'}),
            'gender' : forms.Select(choices=gender_choices),
            'date_Of_birth' : forms.DateInput(attrs = {'type': 'date','class':'form-control'}),
        }

class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email','class':'form-control','type':'text'}))
    username=forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'username','class':'form-control','type':'text'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Email','class':'form-control','type':'email'}))
    password1 = forms.RegexField(label=("Password"),widget=forms.PasswordInput(attrs={'placeholder': 'Enter your Password ','onkeyup': 'passwordStrength(this.value)','class':'form-control'}),regex=r'^.*(?=.{6,})(?=.*[a-z]).*$')
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={'placeholder': 'ReEnter password ','class':'form-control'}))

    class Meta:
        model = User
        fields = ("first_name","last_name","email", "password1", "password2")
        widgets = {
            "first_name" : forms.TextInput(attrs = {'type': 'text','class':'form-control'}),
            "last_name" : forms.TextInput(attrs = {'type': 'text','class':'form-control'}),

        }

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name=self.cleaned_data["first_name"]
        user.last_name=self.cleaned_data["last_name"]

        if commit:
            user.save()
        return user