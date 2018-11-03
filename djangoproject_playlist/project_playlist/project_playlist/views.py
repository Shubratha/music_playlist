from django.shortcuts import render, redirect
from django.contrib.auth  import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from .models import Playlist,Song
from django.http import JsonResponse
from rest_framework.views import APIView
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import generics
from project_playlist.serializers import PlaylistSerializer, SongSerializer, UserSerializer
from project_playlist.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions
import requests
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework import pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# class LargeResultsSetPagination(PageNumberPagination):
#     page_size = 2
#     page_size_query_param = 'page_size'
#     max_page_size = 5

def signup(request):
    if request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'project_playlist/signup.html', {'form': form})
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
        if not form.is_valid():
            return HttpResponse(form.errors)
        form.save()
        user= User.objects.get(username= form.cleaned_data.get('username'))
        login(request, user)
        return render(request, 'project_playlist/signup.html', {'form': form})
    else:
        return HttpResponse("Unsupported method")

def login_view(request):
    if request.method == 'GET':
        if not request.user.is_anonymous:
            return redirect('/playlists')
        else:
            form = AuthenticationForm()
            return render(request, 'project_playlist/login.html', {'form': form})
    elif request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/playlists')
        else:
            return render(request, 'project_playlist/login.html', {'form': form})


def log_out(request):
    logout(request)
    return HttpResponseRedirect("/login/")


def get_playlist(request,playlist_id):
    #import pdb; pdb.set_trace()
    if request.method == 'GET':
        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except Playlist.DoesNotExist:
            return HttpResponse("Playlist not available",content_type="text/html", status=400)
        playlist = Playlist.objects.get(id=playlist_id)
        if playlist.user.id == request.user.id:
            context = {'playlist': playlist, 'is_owner':True}
        else:
            context = {'playlist':playlist, 'is_owner':False}
        print(request.user.id)
        print(playlist.user.id)
        songs = Song.objects.all()
        return render(request, 'project_playlist/playlist.html',context)
    elif request.method == 'POST':
        try:
            playlist = Playlist.objects.get(id = playlist_id)
        except Playlist.DoesNotExist:
            return HttpResponse("Playlist not available",content_type="text/html", status=400)
        if playlist.user.id == request.user.id:
            url=request.POST.get('url')
            name=request.POST.get('name')
            if url and name:
                song = Song()
                song.playlist=playlist
                song.url=url
                song.name=name
                song.save()
                return render(request,'project_playlist/playlist.html',{'playlist':playlist})
            else:
                return HttpResponse("Enter song name and valid url")
        else:
            return render(request,'project_playlist/playlist.html',{'playlist':playlist})


def get_all_playlist(request):
    if request.user.is_anonymous:
        return redirect('/login/')
    if request.method == 'GET':
        playlists = Playlist.objects.filter(user=request.user)
        context = {'playlists':playlists} 
        print(request.user)
        return render(request, 'project_playlist/playlists.html',context)
    elif request.method == 'POST':
        title= request.POST.get('title')
        if title:
            Playlist.objects.create(name=title, user=request.user)
            return redirect('/playlists')
        else:
            return HttpResponse("Enter playlist name", status=400)

def list_playlists(request):
    if request.method == 'GET':
        playlists = Playlist.objects.all()
        serializer = PlaylistSerializer(playlists, many=True)
        return JsonResponse(serializer.data,safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PlaylistSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

def list_songs(request, pk):
    try:
        playlist = Playlist.objects.get(pk=pk)
    except Playlist.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = SongSerializer(playlist)
        return JsonResponse(serializer.data)


class Logout(APIView):
    queryset = User.objects.all()

    def get(self, request, format=None):
        # simply delete the token to force a login
        try: 
            request.user.auth_token.delete()
            return Response("Logged out ",status=status.HTTP_200_OK)
        except:
            return Response("No logged in user", status=200)


class ListPlaylists(generics.ListCreateAPIView):
    #import pdb; pdb.set_trace()
    serializer_class = PlaylistSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Playlist.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    def create_playlist(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        print(user)
        return Playlist.objects.filter(user = self.request.user)


class PlaylistDetail(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly,)


    def get_object(self, pk):
        try:
            return Playlist.objects.get(pk=pk)
        except Playlist.DoesNotExist:
            return Response("playlist not found", status=404)

    def get(self, request, pk, format=None):
        # import pdb; pdb.set_trace()
        playlist = Playlist.objects.filter(pk=pk)
        if not len(playlist)==0:
            playlist = playlist[0]
        pID = str(pk)
        uri= "http://localhost:8000/api/playlists/"+pID+ "/?page="
        print(uri)
        if playlist:
            songs = Song.objects.filter(playlist = playlist)
            paginator = Paginator(songs, 3)
            page = request.GET.get('page')
            # page=2
            
            try:
                songs = paginator.page(page)
            except PageNotAnInteger:
            # If page is not an integer, deliver first page.
                songs = paginator.page(1)
            except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
                songs = paginator.page(paginator.num_pages)
            count = paginator.count
            next = None if not songs.has_next() else str(songs.next_page_number())
            prev = None if not songs.has_previous() else str(songs.previous_page_number())
            if next is not None:
                next_page = uri + next
            else:
                next_page = "None"
            if prev is not None:
                prev_page = uri + prev
            else:
                prev_page = "None"
            serializer = SongSerializer(songs, many=True)
            dict ={"count": count, "prev": prev_page, "next": next_page, "serializer": serializer.data}
            return Response(dict, status = 200)
        else:
            return Response("No such playlist exists", status=404)

    def patch(self, request, pk, format=None):
        playlist = self.get_object(pk=pk)
        print(playlist)
        if playlist:
            serializer = PlaylistSerializer(playlist, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("No such playlist exists", status=404)

    def delete(self, request, pk, format=None):
        playlist = self.get_object(pk)
        playlist.delete()
        return Response("Playlist deleted")

class ListSongs(generics.ListCreateAPIView):
    #import pdb; pdb.set_trace()
    serializer_class = SongSerializer
    permission_classes = (permissions.IsAuthenticated,)
    # pagination_class = settings.DEFAULT_PAGINATION_CLASS
    # pagination_class = LargeResultsSetPagination
    # def create(self, serializer):
    #     # if serializer.data['user'] == self.request.user.id:
    #     #     print(self.request.user)
    #     #     print(serializer.playlist.id)
    #     serializer.save(user=self.request.user)
    #     return Response("Song Added" , status = 200)

        # else:
        #     return Response("Not authorised" , status = 401)

    def get_queryset(self):
        user = self.request.user
        print(user)
        return Song.objects.all()

class SongDetail(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly,)
    serializer_class = SongSerializer


    def create_song(self, serializer):
        serializer.save(data=self.request.data)

    def get_object(self, pk):
        try:
            return Song.objects.get(pk=pk)
        except Song.DoesNotExist:
            return Response("Song not found", status=404)

    def get(self, request, pk, format=None):
        try:
            song= Song.objects.get(pk=pk)
        except Song.DoesNotExist:
            return Response("Song not found", status=404)
        serializer = SongSerializer(song)
        print(serializer)
        return Response(serializer.data, status = 200)

    def patch(self, request, pk, format=None):
        song = Song.objects.get(id=pk)
        print(song)
        serializer = SongSerializer(song, data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, pk, format=None):
        song = self.get_object(pk)
        song.delete()
        return Response("Song deleted")

class Userlist(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        if request.user.is_superuser:
            queryset = User.objects.all()
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data, status=200)
        elif request.user.is_anonymous:
            return Response("Anonymous user: Not authorised to view users")
        else:
            queryset = User.objects.get(username=self.request.user)
            print(queryset)
            print(self.request.user)
            serializer = UserSerializer(queryset)
            return Response(serializer.data, status=200)

    def post(self, request): 
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("New user created")
        return Response(serializer.errors)

class UserDetail(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_object(self, pk):
        try:
            return User.objects.get(id=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        queryset = User.objects.get(username = username)
        print(queryset)
        if queryset:
            serializer = UserSerializer(queryset)
            return Response(serializer.data, status = 200)
        else:
            return Response("No such user exists")

    def patch(self, request, pk, format=None):
        user = User.objects.get(pk=pk)
        if request.user.id == user.id:
            serializer = UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = 200)
            else:
                return Response(serializer.errors)
        return Response("Not authorised")


    def delete(self, request, pk, format=None):
        if request.user.is_superuser:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response("User deleted")
        return Response("Not authorised")
