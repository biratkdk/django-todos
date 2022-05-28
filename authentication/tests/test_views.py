from django.urls import reverse
from django.contrib.messages import get_messages

from authentication.models import User
from utils.setup_test import TestSetup


class TestViews(TestSetup):

    def test_should_show_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/register.html")

    def test_should_show_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/login.html")

    def test_should_signup_user(self):
        response = self.client.post(reverse("register"), self.user)
        self.assertEqual(response.status_code, 302)

    def test_should_strip_and_normalize_signup_data(self):
        response = self.client.post(reverse("register"), {
            'username': '  newuser  ',
            'email': '  NEWUSER@app.com  ',
            'password': 'password12!',
            'password2': 'password12!',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser', email='newuser@app.com').exists())

    def test_should_not_signup_user_with_taken_username(self):

        self.user = {
            "username": "username",
            "email": "email@hmail2.com",
            "password": "password",
            "password2": "password"
        }

        self.client.post(reverse("register"), self.user)
        response = self.client.post(reverse("register"), self.user)
        self.assertEqual(response.status_code, 409)

        storage = get_messages(response.wsgi_request)

        self.assertIn("Username is taken, choose another one",
                      list(map(lambda x: x.message, storage)))

    def test_should_not_signup_user_with_taken_email(self):

        self.user = {
            "username": "username1",
            "email": "email@hmail2.com",
            "password": "password",
            "password2": "password"
        }

        self.test_user2 = {
            "username": "username11",
            "email": "email@hmail2.com",
            "password": "password",
            "password2": "password"
        }

        self.client.post(reverse("register"), self.user)
        response = self.client.post(reverse("register"), self.test_user2)
        self.assertEqual(response.status_code, 409)

        storage = get_messages(response.wsgi_request)

        self.assertIn("Email is taken, choose another one",
                      list(map(lambda x: x.message, storage)))

    def test_should_not_signup_user_with_invalid_email(self):
        self.user["email"] = "not-an-email"

        response = self.client.post(reverse("register"), self.user)
        self.assertEqual(response.status_code, 409)

        storage = get_messages(response.wsgi_request)

        self.assertIn("Enter a valid email address",
                      list(map(lambda x: x.message, storage)))

    def test_should_not_signup_user_with_mismatched_passwords(self):
        self.user["password2"] = "different-password"

        response = self.client.post(reverse("register"), self.user)
        self.assertEqual(response.status_code, 409)

        storage = get_messages(response.wsgi_request)

        self.assertIn("Password mismatch",
                      list(map(lambda x: x.message, storage)))

    def test_should_login_successfully(self):
        user = self.create_test_user()
        response = self.client.post(reverse("login"), {
            'username': user.username,
            'password': 'password12!'
        })
        self.assertEqual(response.status_code, 302)

        storage = get_messages(response.wsgi_request)

        self.assertIn(f"Welcome {user.username}",
                      list(map(lambda x: x.message, storage)))

    def test_should_not_login_if_email_is_not_verified(self):
        user = self.create_test_user_two()
        response = self.client.post(reverse("login"), {
            'username': user.username,
            'password': 'password12!'
        })

        self.assertEqual(response.status_code, 401)

        storage = get_messages(response.wsgi_request)

        self.assertIn("Email is not verified, please check your email inbox",
                      list(map(lambda x: x.message, storage)))

    def test_should_not_login_with_invalid_password(self):
        user = self.create_test_user()
        response = self.client.post(reverse("login"), {
            'username': user.username,
            'password': 'password12!32'
        })
        self.assertEqual(response.status_code, 401)

        storage = get_messages(response.wsgi_request)

        self.assertIn("Invalid credentials, try again",
                      list(map(lambda x: x.message, storage)))
