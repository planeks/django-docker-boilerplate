from django.test import TestCase
from ..models import User


class UserTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            'demo@mail.com', 'John Doe', 'demo')
        self.u2 = User.objects.create_superuser(
            'demo2@mail.com', 'Annie Lennox', 'demo')
        self.u3 = User.objects.create_user(
            'robert.downey@mail.com', 'Leslie JJ Mills', 'demo')
        self.u3.save()

    def test_required_fields(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')
        self.assertSequenceEqual(User.REQUIRED_FIELDS, ['name'])

    def test_manager_create_user(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', name='A')
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='', name='A')

    def test_create_user(self):
        u = User.objects.get(email='demo@mail.com')
        self.assertEqual(u.name, 'John Doe')
        self.assertEqual(u.is_staff, False)
        self.assertEqual(u.is_active, True)
        self.assertEqual(u.is_superuser, False)

    def test_str(self):
        self.assertEqual(str(self.u1), 'John Doe')
        self.assertEqual(str(self.u2), 'Annie Lennox')
        self.assertEqual(str(self.u3), 'Leslie JJ Mills')

    def test_has_usable_password(self):
        self.assertTrue(self.u1.has_usable_password())
        self.assertTrue(self.u2.has_usable_password())
        self.assertTrue(self.u3.has_usable_password())
