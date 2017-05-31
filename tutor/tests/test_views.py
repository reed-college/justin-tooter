from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission


class AddUsersTestCase(TestCase):
    """
    Tests for the add_users view
    """

    def test_makes_you_log_in(self):
        """
        Makes sure that you have to log in to the view before
        adding users
        by that, I mean that it just checks if the page redirects
        you
        """
        response = self.client.get(reverse('tutor:add_users'))
        self.assertEqual(response.status_code, 302)

    def test_unauthorized_user_cant_add(self):
        """
        Tests that if you're logged in but unauthorized, then you
        get a 403
        """
        bob = User.objects.create_user("bob", password="bar")
        bob.save()
        self.client.login(username="bob", password="bar")
        # bob doesn't have the right permissions
        response = self.client.get(reverse('tutor:add_users'))
        self.assertEqual(response.status_code, 403)
        bob.delete()

    def test_authorized_user_can_access_add_users(self):
        fred = User.objects.create_user("fred", password="foo")
        # give fred the permissions
        adu = Permission.objects.get(codename='add_user')
        chu = Permission.objects.get(codename='change_user')
        ads = Permission.objects.get(codename='add_student')
        chs = Permission.objects.get(codename='change_student')
        fred.user_permissions.add(adu, chu, ads, chs)
        fred.save()
        # have fred access the page
        self.client.login(username="fred", password="foo")
        response = self.client.get(reverse('tutor:add_users'))
        # Assert that its not an error code
        self.assertTrue(response.status_code < 400)
        self.assertTrue(response.status_code >= 200)
        fred.delete()