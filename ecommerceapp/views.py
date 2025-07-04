from django.shortcuts import render,redirect
from  django.views.generic import View
from django.utils.decorators import method_decorator
from ecommerceapp.decorators import login_required
from ecommerceapp.forms import RegistrationForm,UserProfileForm,LoginForm,BookForm,TagForm,AuthorForm,DeliveryForm,ReviewForm,ContactForm
from ecommerceapp.models import UserProfile,Book,CartItems,Cart,DeliveryDetails,OrderSummary,Author,Review,User,Inquiry,InquiryMessage
from django.contrib.auth import authenticate,login,logout
from ecommerceapp.permissions import SuperUserView
from django.db.models import Q,F
from django.core.paginator import Paginator
from django.urls import reverse

"""   Razor Pay Section """
import razorpay

SECRET_KEY='OQexz5Z5eGtahi8WmWe1D2aJ'     
KEY_ID='rzp_test_qH3eP1u86hcRk9'


class RegistrationView(View):
    def get(self,request,*args,**kwargs):
        form_instance = RegistrationForm()
        return render(request,'registration.html',{'form':form_instance})
    
    def post(self,request,*args,**kwargs):
        form_instance = RegistrationForm(request.POST)
        signup_success = False
        if form_instance.is_valid():
            form_instance.save()
            data = form_instance.cleaned_data
            uname = data.get('username')
            pword = data.get('password1')

            user_obj = authenticate(username=uname,password=pword)
            if user_obj:
                login(request,user_obj)
                signup_success = True
                return render(request,'registration.html',{'signup_success':signup_success})

        return render(request,'registration.html',{'form':form_instance})
    
class LoginView(View):
    def get(self,request,*args,**kwargs):
        form_instance = LoginForm()
        return render(request,'login.html',{'form':form_instance})
    
    def post(self,request,*args,**kwargs):
        form_instance= LoginForm(request.POST)
        if form_instance.is_valid():
            data = form_instance.cleaned_data
            uname = data.get('username')
            pword = data.get('password')
            user_obj = authenticate(username=uname,password=pword)
            if user_obj:
                login(request,user_obj)
            return redirect('home')
        return render(request,'login.html',{'form':form_instance})

class LogoutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('login')

class IndexView(View):
    def get(self, request, *args, **kwargs):
       
            qs = Book.objects.all().order_by('id')
            for book in qs:
                book.is_favorited = book.favourite.filter(id=request.user.id).exists()

            if 'book_id' in request.GET:
                book_id = request.GET.get('book_id')
                book = Book.objects.get(id=book_id)
                if book.favourite.filter(id=request.user.id).exists():
                    book.favourite.remove(request.user)
                else:
                    book.favourite.add(request.user)
                return redirect(f"{reverse('home')}?page={request.GET.get('page', 1)}")

            paginator = Paginator(qs, 8)  # show 8 books per page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'index.html', {'page_obj': page_obj})

@method_decorator(login_required,name='dispatch')                  
class EditProfileView(View):
   
    def get(self,request,*args,**kwargs):
        
            user_id = kwargs.get('pk')
            user_profile = UserProfile.objects.get(user_object=user_id)
            form_instance = UserProfileForm(instance=user_profile)
            return render(request,"edit_profile.html",{'form':form_instance})
        
    
    def post(self,request,*args,**kwargs):
        user_id = kwargs.get("pk")
        user_profile = UserProfile.objects.get(user_object=user_id)
        form_instance = UserProfileForm(request.POST,request.FILES,instance=user_profile)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('home')
        return render(request,'edit_profile.html',{'form':form_instance})


class CreateBookView(SuperUserView,View):

    def get(self,request,*args,**kwargs):
        
     form_instance = BookForm()
     return render(request,'book_add.html',{"form":form_instance})
    
    def post(self,request,*args,**kwargs):
        form_instance = BookForm(request.POST,request.FILES)
        if form_instance.is_valid():
            form_instance.instance.user_object= request.user
            form_instance.save()
            return redirect('dashboard')
        return render(request,'book_add.html',{'form':form_instance})


class BookDetailView(View):

    def get(self,request,*args,**kwargs):
        book_id = kwargs.get('pk')
        book_object = Book.objects.get(id=book_id)
        review_obj = Review.objects.filter(book_object=book_object)
        print(review_obj)
        
        
        related_books = Book.objects.filter(
            tag_obj__in=book_object.tag_obj.all()
        ).exclude(id=book_object.id).distinct()
        print("related:",related_books)
       
        return render(request,'book_detail.html',{'book':book_object,'review':review_obj,'related_books':related_books})
  

class CreateTagView(SuperUserView,View):

    def get(self,request,*args,**kwargs):
        form_instance= TagForm()
        return render(request,'tag_create.html',{'form':form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance = TagForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('book-create')
        return render(request,'tag_create.html',{'form':form_instance})

class CreateAuthorView(SuperUserView,View):

    def get(self,request,*args,**kwargs):
        form_instance = AuthorForm()
        return render(request,'author_create.html',{'form':form_instance})
        
    def post(self,request,*args,**kwargs):
        form_instance = AuthorForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('book-create')
        return render(request,'author_create.html',{'form':form_instance})
    
@method_decorator(login_required,name='dispatch')    
class AddCartView(View):

    def get(self, request, *args, **kwargs):
        # Get the book ID from URL parameters (e.g., /addtocart/5/)
        book_id = kwargs.get('pk')

        # Fetch the Book object from DB by ID
        book_obj = Book.objects.get(id=book_id)

        # Get the Cart object associated with the logged-in user
        cart_obj = Cart.objects.get(user_object=request.user)

        # Get quantity from URL query params (?quantity=3), default to 1 if not provided
        # Note: request.GET returns strings, so convert to int for calculations
        quantity = int(request.GET.get('quantity', 1))

        # Try to get an existing CartItems object for this book and cart where order not placed
        # If not found, create a new one
        cart_item, created = CartItems.objects.get_or_create(
            book_object=book_obj,
            cart_object=cart_obj,
            is_order_placed=False
        )

        if created:
            # If new cart item created, set its quantity to the requested quantity
            cart_item.quantity = quantity
        else:
            # If cart item exists, increment its quantity by the requested quantity
            cart_item.quantity += quantity

        # Save changes to the CartItems model (update or new record)
        cart_item.save()

        # Redirect user to 'home' page (you can change this to 'cart' or anywhere)
        return redirect('home')

@method_decorator(login_required,name='dispatch')
class CartView(View):

    # Handle GET request to display user's cart
    def get(self, request, *args, **kwargs):

         # Fetch the cart associated with the current logged-in user
            cart = Cart.objects.get(user_object=request.user)
            print("Cart:", cart)

            # Retrieve all cart items that belong to this cart and are not yet ordered
            cart_object = CartItems.objects.filter(cart_object=cart, is_order_placed=False)

            # Get the total price from the cart
            cart_total = cart.total

            print("total amount:", cart_total)

            # Render the cart page with the list of cart items and the total amount
            return render(request, 'cart.html', {'cart': cart_object, 'total': cart_total})

@method_decorator(login_required,name='dispatch')   
class CartItemDeleteView(View):
    def get(self,request,*args,**kwargs):
        cartitem_id = kwargs.get('pk')
        CartItems.objects.get(id=cartitem_id,).delete()
        return redirect('cart')

@method_decorator(login_required,name='dispatch')
class DeliveryView(View):
    def get(self,request,*args,**kwargs):
           
            form_instance = DeliveryForm()           
       
            return render(request,'delivery_details.html',{'form':form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance = DeliveryForm(request.POST)

        if form_instance.is_valid():

            form_instance.instance.user_obj=request.user

            form_instance.save()

            if form_instance.instance.delivery_options == 'cash_on_delivery':
                cart_items = CartItems.objects.filter(cart_object__user_object = request.user,is_order_placed=False)
                for item in cart_items:
                    item.is_order_placed = True
                    item.save()
                return redirect('cash_on_delivery')
            else:
                return redirect('checkout')

        
        return render(request,'delivery_details.html',{'form':form_instance})
    
@method_decorator(login_required,name='dispatch')
class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        client = razorpay.Client(auth=(KEY_ID, SECRET_KEY))

        cart = Cart.objects.get(user_object=request.user)
        amount = cart.total * 100

        print("amount: ", amount)

        data = {
            "amount": amount,
            "currency": "INR",
            "receipt": "order_rcptid_11"
        }
        payment = client.order.create(data=data)

        # print("payment: ", payment)

        data = {
            'order_id': payment.get('id'),
            'amount': payment.get('amount'),
            'key': KEY_ID
        }
        

        cart_items = CartItems.objects.filter(
            is_order_placed=False,
            cart_object__user_object=request.user
        )

        delivery_object = DeliveryDetails.objects.filter(user_obj=request.user)
        # print(delivery_object)

        for del_obj in delivery_object:
            del_obj

        order_obj = OrderSummary.objects.create(
            user_object=request.user,
            order_id=payment.get('id'),
            total=cart.total,
            delivery_obj=del_obj
        )

        for ci in cart_items:
            order_obj.book_object.add(ci.book_object)
            order_obj.save()

        return render(request, 'checkout.html', data)
 

""" 

'razorpay_order_id': razorpay_order_id,
'razorpay_payment_id': razorpay_payment_id,
'razorpay_signature': razorpay_signature

"""
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator 

@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF protection for this view
class PaymentVerificationView(View):
    
    def post(self, request, *args, **kwargs):
        # Print all POST data sent by Razorpay after payment
        print("data via razorpay:", request.POST)

        # Initialize Razorpay client with your API keys
        client = razorpay.Client(auth=(KEY_ID, SECRET_KEY))

        # Get the OrderSummary object by matching razorpay_order_id from POST data

        try:
            ordersummary_id = OrderSummary.objects.get(order_id=request.POST.get('razorpay_order_id'))
            print("order summary object retrieved")
        
        except OrderSummary.DoesNotExist:
            print("order summary object not found")


        # Print current logged-in user (for debugging)
        print("user:", request.user)

        # Log in the user associated with the order (in case not logged in)
        # login(request, ordersummary_id.user_object)

        try:
            # Verify the payment signature to confirm payment authenticity
            client.utility.verify_payment_signature(request.POST)

            # Mark the order as paid
            ordersummary_id.is_paid = True
            ordersummary_id.save()

            # Get all CartItems for this user where order is not yet placed
            cart_items = CartItems.objects.filter(cart_object__user_object=request.user, is_order_placed=False)

            # Loop through each cart item to update stock and mark as ordered
            for ci in cart_items:
                book = ci.book_object
                # Check if enough stock exists before subtracting quantity
                if book.quantity >= ci.quantity:
                    book.quantity -= ci.quantity  # Reduce stock by purchased quantity
                    book.save()

                # Mark this cart item as purchased
                ci.is_order_placed = True
                ci.save()

            print("done")  # Success message

        except:
            print("failed")  # If verification fails or any error occurs

        # Render the payment success page regardless of success/failure in this example
        return render(request, 'payment_success.html')


class AboutView(View):
    def get(self,request,*args,**kwargs):
        return render(request,'about.html')
    
"""
    def post(self,request,*args,**kwargs): 
            form_instance = DeliveryForm(request.POST)
            
            if form_instance.is_valid():
               
                form_instance.save(commit=False)
                form_instance.instance.user_obj=request.user
                a = form_instance.save()
                print("form:",a)
                
                return redirect('checkout')
            return render(request,'delivery_details.html',{'form':form_instance})
"""
   
class BooksSearchView(View):
    def get(self, request, *args, **kwargs):
        active_author = request.GET.get('author')  # Get selected author from query params
        active_query = request.GET.get('q')        # Get search query from query params

        books = Book.objects.none()  # Start with empty queryset

        author = Author.objects.all()  # Get all authors for dropdown

        error_message = None  # Default no error

        # If both author and query are present:
        if active_author and active_query:
            # Filter books by author name matching selected author
            books = Book.objects.filter(author_obj__author_name=active_author)
            # Further filter by book title containing the search query (case-insensitive)
            books = books.filter(title__icontains=active_query)

            # If no books matched, set error message
            if not books.exists():
                error_message = "No matching book found."

        # Render template with variables for books, authors, active filters, and error
        return render(
            request,
            'book_filter.html',
            {
                'books': books,
                'author': author,
                'active_author': active_author,
                'active_query': active_query,
                'error_message': error_message,
            }
        )

@method_decorator(login_required,name='dispatch')        
class BookPaymentHistoryView(View):
    def get(self,request,*args,**kwargs):

            qs = OrderSummary.objects.filter(user_object=request.user,is_paid=True)
            print(qs)
            
            return render(request,'book_pay_history.html',{'qs':qs})
    
@method_decorator(login_required,name='dispatch')  
class BookReviewView(View):
    def get(self,request,*args,**kwargs):
        form_instance = ReviewForm()
        return render(request,'review.html',{'form':form_instance})
    
    def post(self,request,*args,**kwargs):
        book_id = kwargs.get('pk')
        book_object = Book.objects.get(id=book_id) 

        rating_from_hidden_input = request.POST.get('overall_rating')
        
        form_instance = ReviewForm(request.POST)
        if form_instance.is_valid():
            form_instance.instance.user_object = request.user
            form_instance.instance.book_object = book_object
            form_instance.instance.rating  = rating_from_hidden_input
            form_instance.save()
            return redirect('home')
        return render(request,'review.html',{'form':form_instance})
    

        
class DashboardView(SuperUserView,View):
    def get(self,request,*args,**kwargs):
        
       book_obj = Book.objects.all()

       users_count_not_admin = User.objects.filter(is_active=True,is_superuser=False).count()
       book_count = book_obj.count()

       authors = Author.objects.all().count()

       search_query = request.GET.get('search')

       if search_query:
           book_obj = book_obj.filter(Q(title__icontains=search_query)|Q(author_obj__author_name__icontains=search_query))
        
       return render(request,'dashboard.html',{'books':book_obj,'users':users_count_not_admin,'book_count':book_count,'authors_count':authors,"search_query":search_query})    

class BookUpdateView(SuperUserView,View):
    def get(self,request,*args,**kwargs):
        book_id = kwargs.get('pk')
        book_obj = Book.objects.get(id=book_id)
        form_instance = BookForm(instance=book_obj)
        return render(request,'book_update.html',{'form':form_instance})
    
    def post(self,request,*args,**kwargs):
        book_id = kwargs.get('pk')
        book_obj = Book.objects.get(id=book_id)
        form_instance = BookForm(request.POST,instance=book_obj)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('dashboard')
        
class BookDeleteView(SuperUserView,View):
    def get(self,request,*args,**kwargs):
        book_id = kwargs.get('pk')
        Book.objects.get(id=book_id).delete()
        return redirect('dashboard')
    

class NOPermissionView(View):
    def get(self,request,*args,**kwargs):
        return render(request,'no_permission.html')

class BookListView(SuperUserView,View):
    def get(self,request,*args,**kwargs):
        books = Book.objects.all()
        return render(request,'book_list.html',{'books':books})
    
@method_decorator(login_required,name='dispatch')
class BookFavouritesView(View):
    def get(self,request,*args,**kwargs):
 
        favourite_books = Book.objects.filter(favourite=request.user)
        print(favourite_books)
        return render(request,'book_favourite.html',{'favourite_books':favourite_books})

@method_decorator(login_required,name='dispatch')
class BookFavouriteDeleteView(View):
    def get(self,request,*args,**kwargs):
        book_id = kwargs.get('pk')
        book_object = Book.objects.get(id=book_id)
        book_object.favourite.remove(request.user)
        return redirect('favourite_books')
    
@method_decorator(login_required,name='dispatch')
class BookProfileView(View):
    def get(self,request,*args,**kwargs):
        return render(request,'profile.html')

    
class CashOnDeliveryView(View):
    def get(self,request,*args,**kwargs):
        return render(request,'cash_on_delivery.html')
    

class ContactUsView(View):

    def get(self,request,*args,**kwargs):
        return render(request,'contactus.html')

    def post(self,request,*args,**kwargs):
        countryCode = request.POST.get('countryCode')
        form_instance = ContactForm(request.POST)
        if form_instance.is_valid():
          inquiry = form_instance.cleaned_data
          phone = inquiry.get('phone')
          form_instance.instance.phone = f'{countryCode+phone}'

         

          if request.user.is_authenticated:
              form_instance.instance.user = request.user 

        
              
          form_instance.save()
        return render(request,'contactus.html')
    
from django.views import View
from django.shortcuts import render, redirect
from .models import Inquiry, InquiryMessage

class LiveChatView(View):
    
    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect('login')  # or handle anonymous live chat with session key if needed

        # 🔄 Step 0: Link all previous anonymous inquiries (with same email) to this user
        Inquiry.objects.filter(user=None, email=user.email).update(user=user)

        # 📌 Step 1: Get the earliest inquiry by this user
        inquiry = Inquiry.objects.filter(user=user).order_by('created_at').first()

        if not inquiry:
            return render(request, "livechat.html", {
                'error': "No previous inquiry found. Please contact us first."
            })

        # ✉️ Step 2: Save original inquiry message as the first chat message if not done yet
        if inquiry.message and not InquiryMessage.objects.filter(inquiry=inquiry).exists():
            InquiryMessage.objects.create(
                inquiry=inquiry,
                sender=user,
                content=inquiry.message
            )

        # 💬 Step 3: Get all messages for this inquiry
        messages = InquiryMessage.objects.filter(inquiry=inquiry).order_by('created_at')

        return render(request, "livechat.html", {
            'inquiry': inquiry,
            'messages': messages
        })

    def post(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect('login')  # optional protection

        content = request.POST.get('content')

        # 🧾 Use the first inquiry made by the logged-in user
        inquiry = Inquiry.objects.filter(user=user).order_by('created_at').first()

        if inquiry and content:
            InquiryMessage.objects.create(
                inquiry=inquiry,
                sender=user,
                content=content
            )

        return redirect('livechat')

       
                         



from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

@method_decorator(staff_member_required, name='dispatch')
class AdminChatDetailView(View):
    def get(self, request, inquiry_id):
        inquiry = Inquiry.objects.get(id=inquiry_id)
        messages = InquiryMessage.objects.filter(inquiry=inquiry).order_by('created_at')
        return render(request, "admin_chat_detail.html", {
            'inquiry': inquiry,
            'messages': messages
        })

    def post(self, request, inquiry_id):
        inquiry = Inquiry.objects.get(id=inquiry_id)
        content = request.POST.get('content')

        if content:
            InquiryMessage.objects.create(
                inquiry=inquiry,
                sender=request.user,  # This will be the admin
                content=content
            )

        return redirect('admin_chat_detail', inquiry_id=inquiry.id)

        





