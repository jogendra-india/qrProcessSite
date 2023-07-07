"""qrSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from mainQR.views import loginPage,index,logoutUser,homepage,download_file,liveStatus, download_exe, setup_database
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login',loginPage,name='login'),
    path('index/<str:id>',index,name="index_page"),
    path('home/<str:id>',homepage,name="home_page"),
    path('downloadOracle/', download_file,name="download_oracle"),
    path('downloadexe/<str:id>/', download_exe, name="download_exe"),
    path('downloadexe/<str:id>', download_exe),
    path('setupdatabase/', setup_database, name='setup-database'),
    path('live/<str:id1>',liveStatus,name="live_status"),
    path('logout', logoutUser,name='logout'),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
