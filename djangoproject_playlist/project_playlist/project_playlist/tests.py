from django.test import TestCase
from .models import Playlist,Song
from django.utils import timezone
from django.test import Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

class LoginTest(TestCase):
    def setUp(self):
        users = [
            {
                "username": "dexter",
                "password": "Dexter@123",
                "email": "dexter@gmail.com"
            },
            {
                "username": "peeta",
                "password": "Peeta@123",
                "email": "peetam@gmail.com"
            }
        ]
        for user in users:
            u = User.objects.create_user(user['username'], user['password'], user['email'])
        User.objects.create_superuser(username="shubratha", password="shub@123",email="shubratha@codekraft.in")

    def test_login_get(self):
        client = Client()
        response = client.get('/login')
        self.assertEqual(response.status_code, 301)

        response = client.get('/')
        self.assertEqual(response.status_code, 404)

    def test_login_post(self):
        client = Client()
        response = client.post('/api/login/', {'username': 'shubratha', 'password': 'shub@123'})
        self.assertEqual(response.status_code, 200)
        response = client.get('/')
        self.assertEqual(response.status_code, 404)
        response = client.get('/login')
        self.assertEqual(response.status_code, 301)

    def test_login_afterlogin(self):
        client = Client()
        response = client.post('/login', {'username': 'shubratha', 'password': 'Shub@123'})
        self.assertEqual(response.status_code, 301)
        response = client.get('/login')
        self.assertEqual(response.status_code, 301)

    def test_login_invaliduser(self):
        client = Client()
        response = client.post('/login', {'username': 'dfdf', 'password': 'erere'})
        self.assertEqual(response.status_code,301)
        response = client.get('/')
        self.assertEqual(response.status_code, 404)

class LogoutTest(TestCase):
    def setUp(self):
        users = [
            {
                "username": "dexter",
                "password": "Dexter@123",
                "email": "dexter@gmail.com"
            },
            {
                "username": "peeta",
                "password": "Peeta@123",
                "email": "peetam@gmail.com"
            }
        ]
        for user in users:
            u = User.objects.create_user(user['username'], user['password'], user['email'])
        User.objects.create_superuser(username="shubratha", password="Shub@123", email="shubratha@codekraft.in")

    def test_logout_get(self):
        client = Client()
        response = client.post('/api/login/', {'username': 'shubratha', 'password': 'Shub@123'})
        self.assertEqual(response.status_code, 200)
        # response = client.get('/')
        # self.assertEqual(response.status_code, 404)
        response = client.get("/api/logout/")
        self.assertEqual(response.status_code, 200)

    def test_logout_invalidmethod(self):
        client = Client()
        response = client.post('/api/login/', {'username': 'shubra', 'password': 'Shub@123'})
        self.assertEqual(response.status_code, 400)
        response = client.post("'/api/logout/'")
        self.assertEqual(response.status_code, 404) 

class UserAPITest(TestCase):
    def setUp(self):
        users = [
            {
                "username": "dexter",
                "password": "Dexter@123",
                "email": "dexter@gmail.com"
            },
            {
                "username": "peeta",
                "password": "Peeta@123",
                "email": "peetam@gmail.com"
            }
        ]
        for user in users:
            u = User.objects.create_user(user['username'], user['password'], user['email'])
            Token.objects.get_or_create(user=u)
        User.objects.create_superuser(username="hello", password="hello@123", email="hello@gmail.com")

    def test_authorization_test_invalid(self): 
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + '')
        response = client.get("/api/playlists/")
        self.assertEqual(response.status_code, 401)

    def test_authorization_test_valid(self):
        token = Token.objects.first()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + '{}'.format(token.key))
        response = client.get("/api/playlists/")
        self.assertEqual(response.status_code, 200)
        token = Token.objects.last()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + '{}'.format(token.key))
        response = client.get("/api/playlists/")
        self.assertEqual(response.status_code, 200)  

class PlaylistAPITest(TestCase):
    def setUp(self):
        users = [
            {
                "username": "dexter",
                "password": "Dexter@123",
                "email": "dexter@gmail.com"
            },
            {
                "username": "peeta",
                "password": "Peeta@123",
                "email": "peetam@gmail.com"
            }
        ]
        for user in users:
            u = User.objects.create_user(user['username'], user['password'], user['email'])
            # Token.objects.get_or_create(user=u)
        User.objects.create_superuser(username="hello", password="hello@123", email="hello@gmail.com")

    def test_valid_test_cases_api(self):
        client = APIClient()
        response = client.post('/api/login/', {'username': 'hello', 'password':'hello@123'})
        self.assertEqual(response.status_code,200)
        token = Token.objects.get(user=User.objects.get(username="hello"))
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get('/api/playlists/', format='json')
        self.assertEqual(response.status_code, 200)
        response = client.post('/api/playlists/', {'name': 'new-playlist'}, format='json')
        self.assertEqual(response.status_code, 201)
        response = client.get('/api/playlists/1/', format='json')
        self.assertEqual(response.status_code, 200)
        response = client.patch('/api/playlists/1/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        response = client.patch('/api/playlists/1/', {'name': 'newPlaylist'}, format='json')
        self.assertEqual(response.status_code, 200)
        response = client.get('/api/songs/', format='json')
        self.assertEqual(response.status_code, 200)
        response = client.post('/api/songs/', {'playlist': 1, 'url': 'https://www.youtube.com/watch?v=207X6DTY4LY', 'name': 'you are the reason'}, format='json')
        self.assertEqual(response.status_code, 201)
        response = client.delete('/api/playlists/1/', format='json')
        self.assertEqual(response.status_code, 200)

    def test_invalid_test_cases_api(self):
        client = APIClient()
        response = client.post('/api/login/', {'username': 'hello', 'password':'hello@123'})
        self.assertEqual(response.status_code,200)
        token = Token.objects.get(user=User.objects.get(username="hello"))
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = client.get('/api/plaists/', format='json')
        self.assertEqual(response.status_code, 404)
        response = client.patch('/api/playlists/', { 'name': 'you are the reason'}, format='json')
        self.assertEqual(response.status_code, 405)
        response = client.delete('/api/playlists/', format='json')
        self.assertEqual(response.status_code, 405)
        response = client.get('/api/playlists/1/', {}, format='json')
        self.assertEqual(response.status_code, 404)
        response = client.get('/api/songs/1/', format='json')
        self.assertEqual(response.status_code, 404)
        response = client.post('/api/songs/', { 'url': 'https://www.youtube.com/watch?v=207X6DTY4LY', 'name': 'you are the reason'}, format='json')
        self.assertEqual(response.status_code, 400)
        response = client.patch('/api/songs/', { 'url': 'https://www.youtube.com/watch?v=207X6DTY4LY', 'name': 'you are the reason'}, format='json')
        self.assertEqual(response.status_code, 405)

class PlaylistUITest(TestCase):
    def setUp(self):
        users = [
            {
                "username": "dexter",
                "password": "Dexter@123",
                "email": "dexter@gmail.com"
            },
            {
                "username": "peeta",
                "password": "Peeta@123",
                "email": "peetam@gmail.com"
            }
        ]
        for user in users:
            u = User.objects.create_user(user['username'], user['password'], user['email'])
        User.objects.create_superuser(username="shubratha", password="Shub@123", email="shubratha@codekraft.in")

    def test_valid_test_cases_ui(self):
        client = Client()
        response = client.post('/login/', {'username': 'shubratha', 'password': 'Shub@123'})
        response = client.get('/playlists')
        
        
        self.assertEqual(response.status_code, 200)
        response = client.post('/playlists', { 'title': 'party'})
        self.assertEqual(response.status_code, 302)
        response = client.get('/playlist/1')
        self.assertEqual(response.status_code, 200)
        response = client.post('/playlist/1', {'url': 'https://www.youtube.com/watch?v=aJOTlE1K90k', 'name':'Girls like you'})
        self.assertEqual(Playlist.objects.filter(name='party').count(), 1)
        self.assertEqual(Song.objects.filter(name='Girls like you').count(), 1)

        # self.assertEqual(response.status_code, 200)
    def test_invalid_test_cases_ui(self):
        client = Client()
        response = client.post('/login/', {'username': 'shubratha', 'password': 'Shub@123'})
        response = client.post('/playlists', {})
        print("*************************")
        print(response)
        print(response.content)
        print("*********************")
        self.assertEqual(response.status_code, 400)
        response = client.get('/playlist/1')
        self.assertEqual(response.status_code, 400)
        response = client.post('/playlist/1')
        self.assertEqual(response.status_code, 400)



        



# class User_Form_Test(TestCase):

#     # Valid Form Data
#     def test_UserForm_valid(self):
#         form = UserForm(data={'username': "user1", 'password': "user@123"})
#         self.assertTrue(form.is_valid())

#     # Invalid Form Data
#     def test_UserForm_invalid(self):
#         form = UserForm(data={'username': "", 'password': "mp"})
#         self.assertFalse(form.is_valid())

# class User_Views_Test(SetUp_Class):

#     def test_home_view(self):
#         user_login = self.client.login(username="user1", password="user@123")
#         self.assertTrue(user_login)
#         response = self.client.get("/")
#         self.assertEqual(response.status_code, 302)

#     def test_add_user_view(self):
#         response = self.client.get("include url for add user view")
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "include template name to render the response")

#     # Invalid Data
#     def test_add_user_invalidform_view(self):
#         response = self.client.post("include url to post the data given", {'username': "user1", 'email': "admin@mp.com", 'password': "", 'first_name': "mp"})
#         self.assertTrue('"error": true' in response.content)

#     # Valid Data
#     def test_add_admin_form_view(self):
#         user_count = User.objects.count()
#         response = self.client.post("include url to post the data given", {'username': "user1", 'email': "user@mp.com", 'password': "user", 'first_name': "user"})
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(User.objects.count(), user_count+1)
#         self.assertTrue('"error": false' in response.content)


