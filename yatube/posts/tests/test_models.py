from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User

USERNAME = "test_user"
TEST_GROUP_SLUG = "test_group"
TEST_GROUP_NAME = "test_group"
TEST_POST_TEXT = "This is a test text"
USERNAME_2 = "username_2"
COMMENT_TEXT = "This is a test comment to be tested"


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


class CommentModelTest(TestCase):
    """Tests the Comment model"""
    @classmethod
    def setUpClass(cls):
        """Creation of test users, test posts and test comments"""
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.post = Post.objects.create(
            text=TEST_POST_TEXT,
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text=COMMENT_TEXT,
            author=cls.user_2
        )

    def test_comment_str(self):
        comment = self.comment
        string = comment.__str__()
        expected_string = COMMENT_TEXT[:15]
        self.assertEqual(string, expected_string)


class FollowModelTest(TestCase):
    """Tests the Follow model"""
    @classmethod
    def setUpClass(cls):
        """Creating two test users and a test following"""
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_2
        )

    def test_follow_str(self):
        """tests if the __str__ method works as it should"""
        follow = self.follow
        string = follow.__str__()
        expected_string = f"{self.user} following {self.user_2}"
        self.assertEqual(string, expected_string)
