from django.test import TestCase

from posts.models import Group, Post, User

USERNAME = "test_user"
TEST_GROUP_SLUG = "test_group"
TEST_GROUP_NAME = "test_group"
TEST_POST_TEXT = "This is a test text"


class PostModelTest(TestCase):
    """Tests the models of the app"""
    @classmethod
    def setUpClass(cls):
        """Creation of a test user and a test post"""
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.post = Post.objects.create(
            text=TEST_POST_TEXT,
            author=cls.user
        )

    def test_str_title(self):
        """Tests if the __str__ method of the post
        model works correctly"""
        post = self.post
        string = post.__str__()
        expected_string = post.text[:15]
        self.assertEqual(string, expected_string)


class GroupModelTest(TestCase):
    """Tests the group model"""
    @classmethod
    def setUpClass(cls):
        """Creation of a test group"""
        super().setUpClass()
        cls.group = Group.objects.create(
            title=TEST_GROUP_NAME,
            slug=TEST_GROUP_SLUG
        )

    def test_group_str(self):
        """Tests the __str__ method of the group model"""
        group = self.group
        string = group.__str__()
        expected_string = group.title
        self.assertEqual(string, expected_string)
