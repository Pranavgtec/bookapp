from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView,UpdateView,CreateView,FormView
from codeapp.forms import RegistrationForm,LoginForm,ProfileForm,ProjectForm,ReviewForm
from django.contrib.auth import authenticate,login,logout
from codeapp.models import UserProfile,Project,WishListItems,OrderSummary,Reviews
from django.db.models import Sum
from django.urls import reverse_lazy
import razorpay # need to import razor pay here
from django.shortcuts import get_object_or_404

# need to install setuptools in terminal to avoid no module named pkg_resources and also install pip install razorpay

SECRET_KEY='OQexz5Z5eGtahi8WmWe1D2aJ'       # put the downloaded secretkey and key_id here 
KEY_ID='rzp_test_qH3eP1u86hcRk9'

# Create your views here.

class RegistrationView(View):
    def get(self,request,*args,**kwargs):
        form_instance = RegistrationForm()
        return render(request,'store/registration.html',{'form':form_instance})
    def post(self,request,*args,**kwargs):
        form_instance = RegistrationForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            data = form_instance.cleaned_data
            uname = data.get('username')  
            pword = data.get('password1')
            user_obj = authenticate(username = uname,password = pword)
            if user_obj:
                login(request,user_obj)
            return redirect('index')
        return render(request,'store/registration.html',{'form':form_instance})
    
class LoginView(View):
    def get(self,request,*args,**kwargs):
        form_instance = LoginForm()
        return render(request,'store/login.html',{'form':form_instance})
    def post(self,request,*args,**kwargs):
        form_instance = LoginForm(request.POST)
        if form_instance.is_valid():
            data = form_instance.cleaned_data
            uname = data.get('username')
            pword = data.get('password')
            obj_data = authenticate(username=uname,password=pword)
            if obj_data:
                login(request,obj_data)
            return redirect('index')
        return render(request,'store/login.html',{'form':form_instance})
    
class LogoutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('login')

class IndexView(TemplateView):

    template_name="store/index.html"

    def get(self,request,*args,**kwargs):
        qs = Project.objects.all().exclude(owner=request.user) # exclude() is used to exclude the logged in user here from home page
        return render(request,self.template_name,{'projects':qs})
    
    

class ProfileEditView(UpdateView):

    model= UserProfile

    form_class= ProfileForm

    template_name= 'store/profile_edit.html'

    success_url=reverse_lazy('index')

class ProjectCreateView(CreateView):

    model = Project
    form_class = ProjectForm
    template_name = 'store/project_add.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.owner = self.request.user  
        return super().form_valid(form)  

class MyProjectListView(View):
    def get(self,request,*args,**kwargs):
        
        qs =  Project.objects.filter(owner=request.user)

        print(qs)
        
        return render(request,'store/myproject.html',{'works':qs})
    
class ProjectDetailView(View):
    def get(self,request,*args,**kwargs):
        id =  kwargs.get('pk')
        qs = Project.objects.get(id=id)
        return render(request,'store/project_detail.html',{'project':qs})
    
class ProjectDeleteView(View):
    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        Project.objects.get(id=id).delete()
        return redirect('myproject-list')
    
class AddtoWishlistView(View):
    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        qs = Project.objects.get(id=id)
        print(qs)
        
    
        WishListItems.objects.create(wishlist_object=request.user.basket,project_object=qs) # wishlist object is created with project_object because user is related inside wishlist
        return redirect('index')
    

class WishlistView(View):
    def get(self,request,*args,**kwargs):
        # qs = request.user.basket.basket_items.filter(is_order_placed = False)
        qs = WishListItems.objects.filter(wishlist_object__owner=request.user,is_order_placed=False)
        # total=request.user.basket.basket_items.filter(is_order_placed=False).values('project_object__price').aggregate(total=Sum('project_object__price')).get('total')
        total = request.user.basket.wishlist_total 
        
        print("total:",total)
        
        return render(request,'store/wishlist.html',{'qs':qs,"total":total})
    
class WishlistDeleteView(View):
    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        WishListItems.objects.get(id=id).delete()
        return redirect('list-wishlist')
    

class CheckoutView(View):
    def get(self,request,*args,**kwargs):
        
        client = razorpay.Client(auth=(KEY_ID,SECRET_KEY)) # here  pass variables KEYID,SECRET_KEY in razorpay auth , 

        amount  = request.user.basket.wishlist_total*100 # multiply by 100 convert to rupees

        data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" } # here change the amount as with amount variable 

        payment = client.order.create(data=data) # this code is used to create order_id
        print(payment)

        context={
            "amount":payment.get("amount"), # context dictionary used to pass amoutn,order_id,and key to razor pay provided js code
            "order_id":payment.get("id"),
            "key":KEY_ID
        }
        cart_items = request.user.basket.basket_items.filter(is_order_placed=False) # here get the objects that not order placed and pass to loop because of project_object is manytomany
        order_obj = OrderSummary.objects.create(user_object=request.user,order_id=payment.get('id'),total=request.user.basket.wishlist_total) # this code is to add order_id and total to database when press checkout button
        
        
        for ci in cart_items:
            order_obj.project_objects.add(ci.project_object) # add method used because of manytomany
            order_obj.save() 
        return render(request,'store/payment.html',context)
    
from django.views.decorators.csrf import csrf_exempt # is used to done post request without csrf_token

from django.utils.decorators import method_decorator #  is used to make the csrf_token as the method of PaymentVerificationView class
"""
'razorpay_payment_id': ['pay_QPXuzX8eTVBfkR'], 
'razorpay_order_id': ['order_QPXufvA4PGSyaD'], 
'razorpay_signature': ['274eda3b79d071a6b8b16146ef988d6d1dcf99250a3b7646a545732e13027377']
"""
@method_decorator(csrf_exempt,name='dispatch')   # dispatch which decides either get or post
class PaymentVerificationView(View):
    def post(self,request,*args,**kwargs):
        print("Data:",request.POST) # here request.POST contains the data send by the razorpay
        client = razorpay.Client(auth=(KEY_ID, SECRET_KEY))
        user_summary_object = OrderSummary.objects.get(order_id=request.POST.get('razorpay_order_id'))
        login(request,user_summary_object.user_object) # this used because of using csrf_exempt the user may be logout 


        try:


                
            client.utility.verify_payment_signature(request.POST)
            order_id = request.POST.get('razorpay_order_id')
            OrderSummary.objects.filter(order_id=order_id).update(is_paid=True)
            cart_items = request.user.basket.basket_items.filter(is_order_placed=False)
            for ci in cart_items:
                ci.is_order_placed = True
                ci.save()
           

            



            print("done")


        except:

            print("failed")


        return render(request,'store/payment_verify.html')
    
class  MyPurchaseView(View):
    def get(self,request,*args,**kwargs):
        qs = OrderSummary.objects.filter(user_object=request.user,is_paid=True)
        
        return render(request,'store/mypurchase.html',{'qs':qs})



class ReviewView(View):
    def get(self,request,*args,**kwargs):
        form_instance = ReviewForm()
        return render(request,'store/review.html',{'form':form_instance})

    def post(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        qs = Project.objects.get(id=id)
        form_instance = ReviewForm(request.POST)
        if form_instance.is_valid():
            form_instance.instance.user_object=request.user
            form_instance.instance.project_object = qs
           
            form_instance.save()
            
            return redirect('index')
        
        return render(request,'store/review.html',{'form':form_instance})
    



    

       

       
       

