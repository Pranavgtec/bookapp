from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum,F,Avg
# Create your models here.

class UserProfile(models.Model):
    
    user_object = models.OneToOneField(User,on_delete=models.CASCADE)
    bio = models.CharField(max_length=200,null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/',default='/profile_pics/default.png')
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.user_object.username  
    

class Author(models.Model):

    author_name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.author_name

class Tag(models.Model):

    name = models.CharField(max_length=70,unique=True)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name
    

    


class Book(models.Model):

    title = models.CharField(max_length=60)
    book_image = models.ImageField(upload_to='book_pics')
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    # total = models.PositiveBigIntegerField()
    user_object = models.ForeignKey(User,on_delete=models.CASCADE)
    author_obj = models.ForeignKey(Author,on_delete=models.CASCADE)
    tag_obj = models.ManyToManyField(Tag)
    favourite = models.ManyToManyField(User,related_name='favourite',blank=True)

    def __str__(self):
        return self.title
    
    def review_count(self):
        return Review.objects.filter(book_object=self).count()
    @property
    def avg_rating(self):
       avg =  Review.objects.filter(book_object=self).aggregate(avg=Avg('rating')).get('avg')
       return round(avg,2) if avg is not None else None
    
    @property # Use @property to access it like book.star_fills, not book.star_fills()
    def star_fills(self):


        
        if self.avg_rating is None:
            return [0] * 5

        avg = float(self.avg_rating)
        fills = []
        for i in range(1, 6):
            if avg >= i:
                fills.append(100)  # Full star
            elif avg > (i - 1):
                partial_fill = (avg - (i - 1)) * 100
                fills.append(round(partial_fill))  # Partial star
            else:
                fills.append(0)  # Empty star
        return fills


    
    
        
   
        
    
class Cart(models.Model):
    # Each user has one unique cart (OneToOneField means one cart per user)
    user_object = models.OneToOneField(User, on_delete=models.CASCADE)

    # Automatically set the date when the cart is created
    created_date = models.DateField(auto_now_add=True)

    # Automatically update the date when the cart is updated
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.user_object.username

    @property
    def total(self):
        """
        This calculates the total price of items in the cart.
        It filters only those cart items:
        - that belong to this cart (cart_object=self)
        - that have not been ordered yet (is_order_placed=False)

        It then multiplies each book's price by its quantity and adds them all up.
        """
        return CartItems.objects.filter(
            cart_object=self,
            is_order_placed=False
        ).values('book_object__price').aggregate(
            total=Sum(F('book_object__price') * F('quantity'))
        ).get('total')
    
   
    def cart_count(self):
        return CartItems.objects.filter(cart_object=self,is_order_placed=False).count()
    





class CartItems(models.Model):

    book_object = models.ForeignKey(Book,on_delete=models.CASCADE)
    cart_object = models.ForeignKey(Cart,on_delete=models.CASCADE)
    is_order_placed = models.BooleanField(default=False) # this is useful if a user decides to purchase some items now and remaining  later
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.book_object.title

    
class DeliveryDetails(models.Model):
    
    DELIVERY_OPTION = (
        ('cash_on_delivery','cash_on_delivery'),
        ('online payment','online payment')
    )
    name = models.CharField(max_length=70)
    address = models.CharField(max_length=150)
    pincode = models.PositiveIntegerField(null=True)
    phonenumber = models.PositiveIntegerField()
    city = models.CharField(max_length=90)
    state = models.CharField(max_length=80)
    delivery_options = models.CharField(choices=DELIVERY_OPTION,max_length=120)
    user_obj = models.ForeignKey(User,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name
    
    
class OrderSummary(models.Model):

    book_object = models.ManyToManyField(Book)
    user_object = models.ForeignKey(User,on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    delivery_obj = models.ForeignKey(DeliveryDetails,on_delete=models.CASCADE)
    order_id = models.CharField(max_length=255,null=True)
    total = models.IntegerField(null=True)

    def __str__(self):
        return self.user_object.username
    
    

from django.core.validators import MinValueValidator,MaxValueValidator

class Review(models.Model):
    
    book_object = models.ForeignKey(Book,on_delete=models.CASCADE)
    user_object = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.user_object.username                                                                                                        


from django.db import models
from django.contrib.auth.models import User

class Inquiry(models.Model):
    # Link to User if logged in; optional (null and blank allowed)
    # If user is deleted or not found , set this field to NULL but keep the inquiry data
    user = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    
    
 

    # First name of person submitting inquiry - required field
    first_name = models.CharField(max_length=100)
    
    # Last name - required field
    last_name = models.CharField(max_length=100)
    
    # Email - required and validated by EmailField
    email = models.EmailField()
    
    # Phone number - optional, blank allowed in forms
    # No null=True, so empty string stored if not given
    phone = models.CharField(max_length=20, blank=True)
    
    # The main message or inquiry content - required
    message = models.TextField()
    
    # Comma-separated string to store interests/categories selected
    # Required field; you can add blank=True if optional
    interests = models.CharField(max_length=500)
    
    # Timestamp for when inquiry was created, auto-set on insert
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Helpful display in Django admin or shell
        return f"Inquiry from {self.first_name} ({self.email})"


class InquiryMessage(models.Model):
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE) 
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender} at {self.created_at}"

    

    
from django.db.models.signals import post_save

def createprofile(sender,created,instance,*args,**kwargs):
    if created:
        UserProfile.objects.create(user_object=instance)
post_save.connect(sender=User,receiver=createprofile)

def create_cart(sender,created,instance,*args,**kwargs):
    if created:
        Cart.objects.create(user_object=instance)
post_save.connect(sender=User,receiver=create_cart)



    
    

    
    

    

