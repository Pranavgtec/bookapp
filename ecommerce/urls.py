from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ecommerceapp/',include('ecommerceapp.urls')),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # always use + static... in the same line of ']'.

