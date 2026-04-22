from django.shortcuts import render,redirect
from .admin import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import profile

def profile_view(request):
    return render(request,'accounts/profile.html')

def login_view(request):
    if request.method=="POST":
        user= authenticate(request,
                            email=request.POST.get("email"),
                            password=request.POST.get("password")
                            )
        if user is not None:
            login(request,user)
            messages.success(request,"login sucessfull")
            return redirect("profile_page")
        
            print("user exist")
        else:
            messages.error(request,"invalid email or password")
            return redirect('login_page')
    return render(request,'accounts/login.html')
def register(request):
    if request.method=="POST":
        print("this is post",request.POST)
        submitted_form=UserCreationForm(request.POST)
        if submitted_form.is_valid():
            registered_user=submitted_form.save()
            profile.objects.create(
                user=registered_user
            )
            messages.success(request,"Registration sucessfull.Please login and verify kyc")
            return redirect("login_page")
        else:
            print("not valid")
            messages.error(request,"email already taken")
        return redirect("register_page")
    
    return render(request,'accounts/register.html')

def logout_view(request):
    logout(request)
    messages.success(request,"logout sucessfull")
    return redirect('login_page')


# Create your views here.
