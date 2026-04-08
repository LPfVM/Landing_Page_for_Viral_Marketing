from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("users/signup/", views.UserSignUpView.as_view(), name="user_signup"),
    path("users/verify/", views.EmailVerifyView.as_view(), name="email_verify"),
    path("users/login/", views.UserLoginView.as_view(), name="user_login"),
    path("users/<int:pk>/", views.UserProfileView.as_view(), name="user_profile"),
]
