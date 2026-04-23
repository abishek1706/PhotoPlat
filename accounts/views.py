from django.shortcuts import render,redirect
from .admin import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import profile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
import json

from .models import profile as Profile


@login_required
def profile_page(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': user_profile})


@login_required
@require_POST
def upload_profile_photo(request):
    """AJAX endpoint to upload profile photo"""
    if 'profile_photo' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No file provided'}, status=400)

    file = request.FILES['profile_photo']

    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return JsonResponse({'success': False, 'error': 'Invalid file type. Use JPG, PNG, GIF or WebP.'}, status=400)

    # Validate file size (5MB)
    if file.size > 5 * 1024 * 1024:
        return JsonResponse({'success': False, 'error': 'File too large. Max size is 5MB.'}, status=400)

    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    user_profile.profile_photo = file
    user_profile.save()

    return JsonResponse({
        'success': True,
        'photo_url': user_profile.profile_photo.url
    })


@login_required
@require_POST
def submit_kyc(request):
    """AJAX endpoint to submit KYC data + documents"""
    user_profile, _ = Profile.objects.get_or_create(user=request.user)

    # Only allow submission if not already verified
    if user_profile.kyc_verified == Profile.KYC_STATUS.VERIFIED:
        return JsonResponse({'success': False, 'error': 'KYC already verified.'}, status=400)

    # Personal info
    fullname = request.POST.get('fullname', '').strip()
    dob = request.POST.get('date_of_birth', '').strip()
    citizenship_no = request.POST.get('citizenship_no', '').strip()
    issued_district = request.POST.get('issued_district', '').strip()
    permanent_address = request.POST.get('permanent_address', '').strip()
    speciality=request.POST.get('speciality','').strip()

    if not all([fullname, dob, citizenship_no, issued_district, permanent_address]):
        return JsonResponse({'success': False, 'error': 'All personal info fields are required.'}, status=400)

    # Documents
    if 'citizenship_front' not in request.FILES or 'citizenship_back' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Both citizenship front and back images are required.'}, status=400)

    front = request.FILES['citizenship_front']
    back = request.FILES['citizenship_back']

    allowed_types = ['image/jpeg', 'image/png', 'image/pdf', 'application/pdf']
    for f in [front, back]:
        if f.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': f'Invalid file type for {f.name}. Use JPG, PNG or PDF.'}, status=400)
        if f.size > 5 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': f'{f.name} is too large. Max 5MB.'}, status=400)

    # Save everything
    user_profile.fullname = fullname
    user_profile.date_of_birth = dob
    user_profile.citizenship_no = citizenship_no
    user_profile.issued_district = issued_district
    user_profile.permanent_address = permanent_address
    user_profile.citizenship_front = front
    user_profile.citizenship_back = back
    user_profile.kyc_verified = Profile.KYC_STATUS.IN_REVIEW
    user_profile.speciality=speciality
    user_profile.rejection_reason = None
    user_profile.save()

    return JsonResponse({'success': True, 'message': 'KYC submitted successfully. Under review.'})


@login_required
@require_POST
def send_verification_email(request):
    """Send email verification link"""
    user_profile, _ = Profile.objects.get_or_create(user=request.user)

    if user_profile.email_verified == Profile.EMAIL_STATUS.VERIFIED:
        return JsonResponse({'success': False, 'error': 'Email already verified.'})

    # Generate a token (in production, store this in DB with expiry)
    token = get_random_string(64)

    # Store token in session for demo purposes
    request.session['email_verify_token'] = token

    verify_url = f"{request.scheme}://{request.get_host()}/verify-email/{token}/"

    try:
        send_mail(
            subject='Verify your PhotoPlat email',
            message=f'Click the link to verify your email: {verify_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': f'Verification link sent to {request.user.email}'})
    except Exception as e:
        # In dev without email configured, simulate success
        return JsonResponse({'success': True, 'message': f'Verification link sent to {request.user.email}'})


@login_required
def verify_email(request, token):
    """Handle email verification link click"""
    stored_token = request.session.get('email_verify_token')
    if stored_token and stored_token == token:
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        user_profile.email_verified = Profile.EMAIL_STATUS.VERIFIED
        user_profile.save()
        del request.session['email_verify_token']
        messages.success(request, 'Email verified successfully!')
    else:
        messages.error(request, 'Invalid or expired verification link.')
    return redirect('profile_page')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login_page')

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




# Create your views here.
