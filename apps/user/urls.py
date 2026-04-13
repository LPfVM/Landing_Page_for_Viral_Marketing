from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    # 유저 관련
    path("users/signup/", views.UserSignUpView.as_view(), name="user_signup"),
    path("users/verify/", views.EmailVerifyView.as_view(), name="email_verify"),
    path("users/login/", views.UserLoginView.as_view(), name="user_login"),
    path("users/logout/", views.UserLogoutView.as_view(), name="user_logout"),
    path("users/<int:pk>/", views.UserProfileView.as_view(), name="user_profile"),
    # jwt
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", views.UserRefreshTokenView.as_view(), name="token_refresh"),
    path("token/verify/", views.CustomTokenVerifyView.as_view(), name="token_verify"),
]
