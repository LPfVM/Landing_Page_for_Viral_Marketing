from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    # User
    path("users/signup/", views.UserSignUpView.as_view(), name="user_signup"),
    path("users/verify/", views.EmailVerifyView.as_view(), name="email_verify"),
    path("users/<int:pk>/", views.UserProfileView.as_view(), name="user_profile"),
    # Auth
    path("users/login/", views.UserLoginView.as_view(), name="user_login"),
    path("users/logout/", views.UserLogoutView.as_view(), name="user_logout"),
    path("token/refresh/", views.UserRefreshTokenView.as_view(), name="token_refresh"),
    # TokenObtainPairView는 커스터마이징한 로그인 기능과 겹치기 때문에 삭제
    # DEFAULT_AUTHENTICATION_CLASSES에서 토큰 검사를 하고 있어서 주석처리
    # path("token/verify/", views.CustomTokenVerifyView.as_view(), name="token_verify"),
]
