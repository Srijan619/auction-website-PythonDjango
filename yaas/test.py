from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
import uuid
from auction.models import Auction

class AdditionalTest(TestCase):
    def setUp(self):
        # setUp run before every test method

        self.userinfo={
            "username": "testUser3",
            "password": "123",
            "email": "user1@gmail.com"
        }
        self.uuid=uuid.uuid4()
        self.data_auction = {
            "title": "newItem",
            "description": "something",
            "minimum_price": 10,
            "deadline_date": (timezone.now() + timezone.timedelta(days=5)).strftime("%d.%m.%Y %H:%M:%S")
        }


        self.data = {
            "title": "item1",
            "description": "new content"
        }

        pass

    def test_store_language(self):
        lang_code="sv"
        # change users default language preference to swedish
        response2 = self.client.get(reverse("changeLanguage", args=(lang_code,)))

        #sign up new user with the details and language preference
        response1 = self.client.post(reverse("signup"), self.userinfo)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.status_code, 302)

        #sign in user
        response3=self.client.post(reverse("signin"), self.userinfo)
        self.assertEqual(response3.status_code, 302)

        #check if the language preference is changed
        response4 = self.client.get(reverse("auction:index"))
        self.assertContains(response4,"lista över tillgängliga auktioner")

    def test_concurrent_users(self):
        user2info = {
            "username": "testUser1",
            "password": "1234",
            "email": "testuser@gmail.com"
        }

        self.item1_id = 1

        # creating two new users
        user1_signup = self.client.post(reverse("signup"), self.userinfo)
        user2_signup = self.client.post(reverse("signup"), user2info)
        self.assertEqual(user1_signup.status_code, 302)
        self.assertEqual(user2_signup.status_code, 302)

        # sign in first user
        user1_signin = self.client.post(reverse("signin"), self.userinfo)
        self.assertEqual(user1_signin.status_code, 302)

        # First user creates new auction
        user1_auction_create = self.client.post(reverse("auction:create"), self.data_auction, follow=True)
        self.assertEqual(user1_auction_create.redirect_chain[0][1], 302)  # check redirect
        self.assertContains(user1_auction_create, "Auction has been created successfully")
        self.client.logout()

        # sign in Second user
        user2_signin = self.client.post(reverse("signin"), user2info)
        self.assertEqual(user2_signin.status_code, 302)

        # Second user gets the bid form for the auction created by first user

        user2_bid_auction = self.client.get(reverse("auction:bid", args=(self.item1_id,)), follow=True)
        self.assertEqual(user2_bid_auction.status_code, 200)
        self.client.logout()

        # User1 signs in again to edit the auction

        # sign in first user
        user1_signin_again = self.client.post(reverse("signin"), self.userinfo)
        self.assertEqual(user1_signin_again.status_code, 302)

        # First User edits the auction

        user1_edit_auction = self.client.post(reverse("auction:edit", args=(self.item1_id,)), self.data, follow=True)
        self.assertEqual(user1_edit_auction.redirect_chain[0][1], 302)
        self.assertContains(user1_edit_auction, "Auction has been updated successfully")
        self.client.logout()

        # second user signs in to bid with old auction data
        user2_signin_again = self.client.post(reverse("signin"), user2info)
        self.assertEqual(user2_signin_again.status_code, 302)

        # second user tries to bid on the old description of the auction before edited
        bidInfo = {
            "new_price": 12
        }
        user2_bid_auction = self.client.post(reverse("auction:bid", args=(self.item1_id,)), bidInfo, follow=True)
        self.assertEqual(user2_bid_auction.status_code, 200)
        self.assertIn(b"You dont have latest information from the auction", user2_bid_auction.content)
        self.client.logout()

    def test_auction_link(self):
        # creating one new users
        user1_signup = self.client.post(reverse("signup"), self.userinfo)
        self.assertEqual(user1_signup.status_code, 302)


        # sign in first user
        user1_signin = self.client.post(reverse("signin"), self.userinfo)
        self.assertEqual(user1_signin.status_code, 302)

        # First user creates new auction

        auction = Auction.objects.create(title="newItem", description="Something", minimum_price=10,
                                              deadline_date=(timezone.now() + timezone.timedelta(days=5)))
        uuid_auction=auction.uuid.hex
        print(uuid_auction)
        self.client.logout() # User is logged out

        # User is logged out and try to get the auction edit form with UUID instead of id where user authentication is not required

        user1_edit_auction = self.client.post(reverse("auction:editlink",  args=(uuid_auction,)),self.data, follow=True)
        self.assertEqual(user1_edit_auction.redirect_chain[0][1], 302)
        self.assertContains(user1_edit_auction, "Auction has been updated successfully") #auction edited without logging in






