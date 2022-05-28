from django.db import IntegrityError

from utils.setup_test import TestSetup
from authentication.models import User


class TestModel(TestSetup):

    def test_should_create_user(self):

        user = self.create_test_user()

        self.assertEqual(str(user), user.email)

    def test_should_store_email_as_lowercase(self):
        user = User.objects.create_user(
            username='EmailUser',
            email='Email@App.com',
            password='password12!',
        )

        self.assertEqual(user.email, 'email@app.com')

    def test_should_enforce_unique_email_in_database(self):
        User.objects.create_user(
            username='username',
            email='email@app.com',
            password='password12!',
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='username-two',
                email='EMAIL@app.com',
                password='password12!',
            )
