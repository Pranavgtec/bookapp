# username: admin , password : user@123
# username: Aravind , password : kadhalrojave

from ecommerceapp.models import UserProfile,Book,Tag,CartItems,Author,Inquiry
from django.contrib import admin


# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Book)
admin.site.register(Tag)
admin.site.register(CartItems)
admin.site.register(Author)
admin.site.register(Inquiry)