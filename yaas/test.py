from django.test import TestCase
from django.urls import reverse

class LanguageTest(TestCase):
    def setUp(self):
        # setUp run before every test method
        pass

    def test_store_language(self):
        lang_code="sv"

        context = {
            "username": "testUser3",
            "password": "123",
            "email": "user1@gmail.com"
        }

        # change users default language preference to swedish
        response2 = self.client.get(reverse("changeLanguage", args=(lang_code,)))

        #sign up new user with the details and language preference
        response1 = self.client.post(reverse("signup"), context)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.status_code, 302)

        #sign in user
        response3=self.client.post(reverse("signin"), context)
        self.assertEqual(response3.status_code, 302)

        #check if the language preference is changed
        response4 = self.client.get(reverse("auction:index"))
        self.assertContains(response4,"lista över tillgängliga auktioner")

