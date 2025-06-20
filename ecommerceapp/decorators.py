from django.shortcuts import redirect

def login_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return fn(request,*args,**kwargs)
    return wrapper

