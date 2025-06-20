from django.db import models

from django.contrib.auth.models import User

from django.db.models import Sum

from django.db import models

from embed_video.fields import EmbedVideoField
# request.user
# UserProfile.objects.get(user_object=request.user)
# USer=>userProfile
# request.user.profile

class UserProfile(models.Model):

    bio=models.CharField(max_length=260,null=True)

    profile_pic=models.ImageField(upload_to="profile_pictures",default="/profile_pictures/default.png")

    user_object=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)


    def __str__(self) -> str:

        return self.user_object.username
    


class Tag(models.Model):

    title=models.CharField(max_length=200,unique=True)
    
    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title
    



class Project(models.Model):

    title=models.CharField(max_length=200)

    description=models.TextField()

    tag_objects=models.ManyToManyField(Tag)

    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name="projects")#related name is used to get user project(request.user.projects) without related name projects.objects.filter(owner=request.user)

    thumbnail=EmbedVideoField()

    price=models.PositiveIntegerField()

    files=models.FileField(upload_to="projects",null=True)
    
    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    def __str__(self):

        return self.title
    
    @property
    def downloads(self):
        return OrderSummary.objects.filter(is_paid=True,project_objects=self).count()
    
    @property
    def reviews(self):
        return Reviews.objects.filter(project_object=self).count()
    




class WishList(models.Model):

    owner=models.OneToOneField(User,on_delete=models.CASCADE,related_name="basket")

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)
    @property # @property is used to make the function as a field of the class
    def wishlist_total(self): # self means the class itself
        return self.basket_items.filter(is_order_placed=False).values('project_object__price').aggregate(total=Sum('project_object__price')).get('total') # get used because total is a dictionary where key is total annd value is amount here totalused as key in get to get value
                                                                                                        # here self means wishlist basket_items means WishlistItems filter used to filter the not order placed product.
# request.user.basket.basket_items.all()
class WishListItems(models.Model):

    wishlist_object=models.ForeignKey(WishList,on_delete=models.CASCADE,related_name="basket_items")

    project_object=models.ForeignKey(Project,on_delete=models.CASCADE)

    is_order_placed=models.BooleanField(default=False)

    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    

class OrderSummary(models.Model):

    user_object=models.ForeignKey(User,on_delete=models.CASCADE,related_name="orders")

    project_objects=models.ManyToManyField(Project)

    order_id=models.CharField(max_length=200,null=True)

    is_paid=models.BooleanField(default=False)
    
    created_date=models.DateTimeField(auto_now_add=True)

    updated_date=models.DateTimeField(auto_now=True)

    is_active=models.BooleanField(default=True)

    total=models.FloatField(null=True)


from django.db.models.signals import post_save# it is used to create something automatically as something created eg profile created when user created

def created_profile(sender,instance,created,*args,**kwargs):# this code for to automatically create profile when user creates

    if created:

        UserProfile.objects.create(user_object=instance)

post_save.connect(sender=User,receiver=created_profile)

def create_basket(sender,instance,created,*args,**kwargs):

    if created:

        WishList.objects.create(owner=instance)

post_save.connect(sender=User,receiver=create_basket)

     

   

from django.core.validators import MaxValueValidator,MinValueValidator

class Reviews(models.Model):

    project_object=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='project_reviews')

    user_object=models.ForeignKey(User,on_delete=models.CASCADE)

    comment=models.TextField()

    rating=models.PositiveIntegerField(default=1,validators=[MaxValueValidator(5),MinValueValidator(1)])

    created_date=models.DateTimeField(auto_now_add=True,null=True)

    updated_date=models.DateTimeField(auto_now=True,null=True)

    is_active=models.BooleanField(default=True,null=True)
