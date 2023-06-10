"""VR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.urls import path
import app.views
from VR import settings

urlpatterns = [
                  path('', app.views.index),
                  path('fregistration', app.views.fregistration),
                  path('login', app.views.login),
                  path('viewfarmers', app.views.viewfarmers),
                  path('viewlabours', app.views.viewlabours),
                  path('uploadtask', app.views.uploadtask),
                  path('changepassfarmer', app.views.changepassfarmer),
                  path('viewtask', app.views.viewtask),
                  path('lregistration', app.views.lregistration),
                  path('alltask', app.views.alltask),
                  path('recommendation', app.views.recommendation),
                  path('work', app.views.work),
                  path('workrequest', app.views.workrequest),
                  path('workassigned', app.views.workassigned),
                  path('ratings', app.views.ratings_),
                  path('changepasslabour', app.views.changepasslabour),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
