from django.urls import path
from .views import AuthView, login_view, register_view, home

urlpatterns = [
    path("", home, name="home"),
    path(
        "auth/login/",
        login_view,
        name="auth-login-basic",
    ),
    path(
        "auth/register/",
        register_view,
        name="auth-register-basic",
    ),
    path(
        "auth/forgot_password/",
        AuthView.as_view(template_name="auth_forgot_password_basic.html"),
        name="auth-forgot-password-basic",
    ),
]
