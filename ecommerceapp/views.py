from django.shortcuts import render,redirect
from  django.views.generic import View

from ecommerceapp.forms import RegistrationForm,UserProfileForm,LoginForm,BookForm,TagForm,AuthorForm,DeliveryForm,ReviewForm
from ecommerceapp.models import UserProfile,Book,CartItems,Cart,DeliveryDetails,OrderSummary,Tag,Author,Review
from django.contrib.auth import authenticate,login,logout
from ecommerceapp.permissions import SuperUserView
from django.db.models import Sum
from django.core.paginator import Paginator

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
        if form_instance.is_valid():
            form_instance.save()
            data = form_instance.cleaned_data
            uname = data.get('username')
            pword = data.get('password1')

            user_obj = authenticate(username=uname,password=pword)
            if user_obj:
                login(request,user_obj)
            return redirect('home')

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
    
    def get(self,request,*args,**kwargs):
        if not request.user.is_authenticated:
           return redirect('login')
 
        else:
             
                
             qs = Book.objects.all().order_by('id')
             
             
             for q in qs:
                 
                 print("data:",q.avg_rating)
                 print("star",q.star_fills)

            
                 
                 

             paginator = Paginator(qs,8) # show 8 books per page


             page_number = request.GET.get('page')
             page_obj = paginator.get_page(page_number)
             print(page_obj)

             

            
             return render(request,'index.html',{'page_obj':page_obj})
                        
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

    
class CartItemDeleteView(View):
    def get(self,request,*args,**kwargs):
        cartitem_id = kwargs.get('pk')
        CartItems.objects.get(id=cartitem_id,).delete()
        return redirect('cart')


class DeliveryView(View):
    def get(self,request,*args,**kwargs):
           
            form_instance = DeliveryForm()           
       
            return render(request,'delivery_details.html',{'form':form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance = DeliveryForm(request.POST)

        if form_instance.is_valid():

            form_instance.instance.user_obj=request.user

            form_instance.save()

            return redirect('checkout')
        
        return render(request,'delivery_details.html',{'form':form_instance})
    
   
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

        print("payment: ", payment)

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
        print(delivery_object)

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
        ordersummary_id = OrderSummary.objects.get(order_id=request.POST.get('razorpay_order_id'))

        # Print current logged-in user (for debugging)
        print("user:", request.user)

        # Log in the user associated with the order (in case not logged in)
        login(request, ordersummary_id.user_object)

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

        
class BookPaymentHistoryView(View):
    def get(self,request,*args,**kwargs):

        
        qs = OrderSummary.objects.filter(user_object=request.user,is_paid=True)
        print(qs)
        
        return render(request,'book_pay_history.html',{'qs':qs})
    
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
          
        
       return render(request,'dashboard.html',{'books':book_obj})    

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
    

    






    

    


    

        
