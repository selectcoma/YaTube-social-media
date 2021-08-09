from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

HOME_PAGE_URL = reverse("index")
GROUP_SLUG = "test_group"
GROUP_URL = reverse("group_posts",
                    kwargs={
                        "slug": GROUP_SLUG
                    })
NEW_POST_URL = reverse("new_post")
NEW_POST_REDIRECT_URL = "/auth/login/?next=/new/"
TEST_GROUP_NAME = "test_group"
TEST_POST_TEXT = "This is a test post"
USERNAME = "test_user"

User = get_user_model()


class PostUrlTest(TestCase):
    """Tests the functioning of the app urls"""
    @classmethod
    def setUpClass(cls):
        """Creation of a test group, test user and a test post"""
        super().setUpClass()
        cls.user = User.objects.create_user(username="test_user")
        cls.group = Group.objects.create(
            title=TEST_GROUP_NAME,
            slug=GROUP_SLUG
        )
        Post.objects.create(
            text=TEST_POST_TEXT,
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        """Creates a guest client and an authorised client
        """
        self.guest_client = Client()
        self.authorized_client = Client()
        self.user = PostUrlTest.user
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Test if homepage url is working"""
        response = self.guest_client.get(HOME_PAGE_URL)
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        """Test if group posts url is working"""
        response = self.guest_client.get(GROUP_URL)
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location(self):
        """Test if new posts creation url is working"""
        response = self.authorized_client.get(NEW_POST_URL)
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirects_guest_user(self):
        """Test if user is redirected to homepage after
        creating a post"""
        response = self.guest_client.get(NEW_POST_URL, follow=True)
        self.assertRedirects(response, NEW_POST_REDIRECT_URL)

    def test_url_uses_correct_template(self):
        """Test if all of the above urls use correct templates"""
        template_url_name = {
            "posts/index.html": HOME_PAGE_URL,
            "posts/group.html": GROUP_URL,
            "posts/new_post.html": NEW_POST_URL
        }
        for template, address in template_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
