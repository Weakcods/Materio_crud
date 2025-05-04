"""
URL configuration for web_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from apps.authentication import views
from web_project.views import SystemView
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    # Authentication URLs first
    path('', redirect_to_login, name='index'),  # Redirect root to login
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', auth_views.LoginView.as_view(
        template_name='auth_forgot_password_basic.html'
    ), name='forgot-password'),
    
    path('admin/', admin.site.urls),
    
    # Protected URLs
    path("dashboard/", include("apps.dashboards.urls")),
    path("", include("apps.layouts.urls")),
    path("", include("apps.pages.urls")),
    path("", include("apps.authentication.urls")),
    path("", include("apps.ui.urls")),
    path("", include("apps.icons.urls")),
    path("", include("apps.forms.urls")),
    path("", include("apps.form_layouts.urls")),
    path("", include("apps.tables.urls")),
    path("", include("pos.urls")),  # Include POS URLs
]

handler404 = SystemView.as_view(template_name="pages_misc_error.html", status=404)
handler400 = SystemView.as_view(template_name="pages_misc_error.html", status=400)
handler500 = SystemView.as_view(template_name="pages_misc_error.html", status=500)
