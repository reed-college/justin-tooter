from django.test import TestCase
from datetime import datetime
from random import randint
import tutor.templatetags.tutor_extras as tutor_extras
from tutor.util import random_string
from django.contrib.auth.models import User
from django_private_chat.models import Dialog, Message


class DatetimeGeTestCase(TestCase):
    """
    tests on the datetime_ge function
    """
    def test_that_one_date_is_greater_than_other(self):
        """
        Pretty silly test, but it will make sure that the function
        has basic functionaliy and doesn't get imported incorectly
        """
        dt1 = datetime(1980, 1, 1)
        dt2 = datetime(1990, 1, 1)
        self.assertTrue(tutor_extras.datetime_ge(dt2, dt1))

class GetVcLinkTestCase(TestCase):
    """
    Tests for the get_vc_link function
    """
    def test_order_of_usernames_doesnt_matter(self):
        """
        Makes sure that the same two usernames passed in different
        orders produces the same link
        """
        username1 = random_string(randint(8, 100))
        username2 = random_string(randint(8, 100))
        link1 = tutor_extras.get_vc_link(username1, username2)
        link2 = tutor_extras.get_vc_link(username2, username1)
        self.assertEqual(link1, link2)

    def test_uniqueness_of_links(self):
        """
        This tests a bunch of usernames and sees if two different
        pairs of usernames generate the same link
        """
        username1 = random_string(randint(8, 100))
        username2 = random_string(randint(8, 100))
        for i in range(0, 100):
            username3 = random_string(randint(8, 100))
            username4 = random_string(randint(8, 100))
            link1 = tutor_extras.get_vc_link(username1, username2)
            link2 = tutor_extras.get_vc_link(username3, username4)
            if (username1 != username3) and (username1 != username4) and (username2 != username3) and (username3 != username4):
                # if there is a collision, with will print out the
                # usernames with the error message
                try:
                    self.assertNotEqual(link1, link2)
                except AssertionError as e:
                    message = "{}\nusername1: {}\nusername2: {}\nusername3: {}\nusername4: {}"
                    message = message.format(e,
                                             username1,
                                             username2,
                                             username3,
                                             username4)
                    raise(AssertionError(message))

            username1 = username3
            username2 = username4


class _mock_dialog:

    def __init__(self, owner, opponent):
        self.owner = owner
        self.opponent = opponent


class _mock_user:

    def __init__(self, username):
        self.username = username


class OtherUsernameTestCase(TestCase):

    def test_basic_functionality(self):
        """
        tests if it will return the opposite username
        """
        j = _mock_user("johnny")
        m = _mock_user("mark")
        d = _mock_dialog(m, j)
        self.assertEqual(tutor_extras.other_username(d, j.username), m.username)
        self.assertEqual(tutor_extras.other_username(d, m.username), j.username)

    def test_throws_error_when_given_invalid_username(self):
        """
        if the passed username is not a memeber of the passed dialog,
        then the function should throw an error
        """
        j = _mock_user("johnny")
        m = _mock_user("mark")
        d = _mock_dialog(m, j)
        with self.assertRaisesMessage(RuntimeError, "Username lisa not present in dialog"):
            tutor_extras.other_username(d, "lisa")


class GetNameTestCase(TestCase):

    def setUp(self):
        self.johnny = User.objects.create_user("johnny")
        self.johnny.first_name = "Johnny"
        self.johnny.last_name = "Wiseau"
        self.johnny.save()

    def tearDown(self):
        self.johnny.delete()

    def test_basic_functionality(self):
        name = tutor_extras.get_name(self.johnny.username)
        self.assertTrue((self.johnny.first_name in name) or
                        (self.johnny.last_name in name))


class GetUserTestCase(TestCase):

    def setUp(self):
        self.johnny = User.objects.create_user("johnny")
        self.johnny.first_name = "Johnny"
        self.johnny.last_name = "Wiseau"
        self.johnny.save()

    def tearDown(self):
        self.johnny.delete()

    def test_basic_functionality(self):
        user = tutor_extras.get_user(self.johnny.username)
        self.assertEqual(self.johnny, user)


class MostRecentMessageTestCase(TestCase):

    def setUp(self):
        self.johnny = User.objects.create_user("johnny")
        self.mark = User.objects.create_user("mark")
        self.dialog = Dialog.objects.create(owner_id=self.johnny.pk, opponent_id=self.mark.pk)
        self.johnny.save()
        self.mark.save()
        self.dialog.save()
        self.m1 = Message.objects.create(dialog_id=self.dialog.pk,
                                         sender_id=self.johnny.id)
        self.m1.text = "I did naht hit her!"
        self.m1.save()
        self.m2 = Message.objects.create(dialog_id=self.dialog.pk,
                                         sender_id=self.johnny.id)
        self.m2.text = "Oh hi Mark"
        self.m2.save()
        self.m3 = Message.objects.create(dialog_id=self.dialog.pk,
                                         sender_id=self.mark.id)
        self.m3.text = "Hey johnny"
        self.m3.save()

    def tearDown(self):
        self.dialog.delete()
        self.mark.delete()
        self.johnny.delete()

    def test_basic_functionality(self):
        """
        makes sure that when you don't pass a username, the
        function returns message 3
        """
        message = tutor_extras.most_recent_message(self.dialog)
        self.assertEqual(self.m3, message)

    def test_second_message_gets_returned(self):
        """
        Makes sure that the function returns the second message
        created by johnny (Oh hi Mark) and not the first (I did
        naht hit her!)
        """
        message = tutor_extras.most_recent_message(self.dialog, self.mark.username)
        self.assertEqual(self.m2, message)

    def test_does_not_return_message_from_given_user(self):
        """
        This makes sure that it does not return a message from
        the user passed to the function
        """
        message = tutor_extras.most_recent_message(self.dialog, self.mark.username)
        self.assertNotEqual(message.sender, self.mark)
        message = tutor_extras.most_recent_message(self.dialog, self.johnny.username)
        self.assertNotEqual(message.sender, self.johnny)
