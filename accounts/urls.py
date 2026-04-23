from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register,name="register_page"),
    path('login/',views.login_view,name="login_page"),
    path('profile/', views.profile_page, name='profile_page'),
    path('profile/upload-photo/', views.upload_profile_photo, name='upload_profile_photo'),
    path('profile/submit-kyc/', views.submit_kyc, name='submit_kyc'),
    path('profile/send-verification/', views.send_verification_email, name='send_verification_email'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
     path('logout/',views.logout_view,name="logout_page")
]
