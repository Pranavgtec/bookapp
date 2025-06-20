from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from codeapp.models import UserProfile,Project,Reviews

class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))
    password2 = forms.CharField(label='Confirm Password',widget = forms.PasswordInput(attrs={'class':'form-control mb-3'}))
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        widgets = {
            'username' : forms.TextInput(attrs={'class':'form-control mb-3'}),
            'email' : forms.EmailInput(attrs={'class':'form-control mb-3'})
        }

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio','profile_pic']
        widgets = {
            'bio' : forms.TextInput( attrs={'class':'w-full border p-2 my-3'}),
            'profile_pic' : forms.FileInput(attrs={'class': 'w-full border p-2 my-3'})
        }
    

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ('owner','created_date','updated_date','is_active') # exclude used to avoid the unneccessary fields and takes the needed field of models to form
        # fields = ['title','description','tag_objects','thumbnail','price','files'] # when using exclude no need to mention fields we need to create a form
        widgets = {
            'title' : forms.TextInput(attrs={'class':'w-full border p-2 my-3'}),
            'description' : forms.TextInput(attrs={'attrs':'w-full border p-2 my-3'}),
            'tag_objects' : forms.SelectMultiple(attrs={'attrs':'w-full border p-2 my-3'}),
            'thumbnail' : forms.TextInput(attrs={'class':'w-full border p-2 my-3'}),
            'price' : forms.NumberInput(attrs={'class':'w-full border p-2 my-3'}),
            'files' : forms.FileInput(attrs={'class':'w-full border p-2 my-3'})
        }



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ['comment','rating']
        widgets = {
            'comment': forms.Textarea(attrs={'class':'form-control mb-3','rows':4,'cols':30}),
            'rating' : forms.TextInput(attrs={'class':' form-control mb-3 '
            })
        }
        







    