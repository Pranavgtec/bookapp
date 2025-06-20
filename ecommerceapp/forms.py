from django import forms
from ecommerceapp.models import UserProfile,Book,Tag,Author,DeliveryDetails,Review,Inquiry
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio','profile_picture']
        widgets = {
            'bio' : forms.TextInput(attrs={'class':'form-control mb-3'}),
            'profile_picture' : forms.FileInput(attrs={'class':'form-control mb-3'})
        }

class RegistrationForm(UserCreationForm):
   password1 = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))
   password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))
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


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control mb-2'})
        }

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['author_name']
        widgets = {
            'author_name' : forms.TextInput(attrs={'class':'form-control mb-2'})
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title','book_image','price','quantity','author_obj','tag_obj']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control mb-2'}),
            'book_image' : forms.FileInput(attrs={'class':'form-control mb-2'}),
            'price' : forms.NumberInput(attrs={'class':'form-control mb-2'}),
            'quantity' : forms.NumberInput(attrs={'class':'form-control mb-2'}),
            'author_obj' : forms.Select(attrs={'class':'form-control mb-2'}),
            'tag_obj' : forms.SelectMultiple(attrs={'class':'form-control mb-2'})

        }
class DeliveryForm(forms.ModelForm):
    class Meta:
        model = DeliveryDetails
        fields = ['name','address','pincode','phonenumber','city','state','delivery_options']
        widgets = {
            'name' : forms.TextInput(attrs={'class':'form-control mb-2'}),
            'address' : forms.Textarea(attrs={'class': 'form-control mb-2' , 'cols' : '8','rows' :'4'}),
            'pincode' : forms.NumberInput(attrs={'class':'form-control mb-2'}),
            'phonenumber': forms.NumberInput(attrs={'class':'form-control mb-2'}),
            'city' : forms.TextInput(attrs={'class':'form-control mb-2'}),
            'state': forms.TextInput(attrs={'class':'form-control mb-2'}),
            'delivery_options' : forms.Select(attrs={'class':'form-control mb-2'})


    }
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']
        widgets = {
            'comment' : forms.TextInput(attrs={'class':'form-control mb-2'}),
           
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['first_name','last_name','email','phone','message','interests']
        