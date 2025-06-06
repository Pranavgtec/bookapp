from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

class SuperUserView(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
         return HttpResponseForbidden("You have no permission to access this page")
        return redirect('login') 

    