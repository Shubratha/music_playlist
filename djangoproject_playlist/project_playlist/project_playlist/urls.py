"""project_playlist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path,re_path
from django.contrib.auth import views as auth_views
from rest_framework.authtoken import views as view
from . import views
from django.conf.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup', views.signup),
    path('login/', views.login_view),
    path('playlist/<int:playlist_id>', views.get_playlist),
    path('playlists', views.get_all_playlist),
    path('logout/',views.log_out),
    path('listsongs/<int:pk>',views.list_songs),
    path('api/playlists/',views.ListPlaylists.as_view()),
    re_path(r'^api/playlists/(?P<pk>[0-9]+)/$',views.PlaylistDetail.as_view()),
    re_path(r'^api/songs/(?P<pk>[0-9]+)/$',views.SongDetail.as_view()),
    path('api/songs/',views.ListSongs.as_view()),
    re_path(r'^api/login/', view.obtain_auth_token),
    re_path(r'^api/logout/', views.Logout.as_view()),
    re_path(r'^api-auth/', include('rest_framework.urls')),
    re_path(r'^api/users/',views.Userlist.as_view()),
    re_path(r'^api/users/(?P<pk>[0-9]+)/$',views.UserDetail.as_view()),
   # path('api/')
]
