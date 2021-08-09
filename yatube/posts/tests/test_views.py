import shutil
import tempfile

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()

INDEX_TEMPLATE = "posts/index.html"
NEW_POST_TEMPLATE = "posts/new_post.html"
GROUP_TEMPLATE = "posts/group.html"
HOMEPAGE_NAME = "index"
HOMEPAGE_URL = reverse(HOMEPAGE_NAME)
GROUP_PAGE_NAME = "group_posts"
GROUP_SLUG = "test_group"
GROUP_SLUG_2 = "test_2_group"
GROUP_URL = reverse(
    "group_posts",
    kwargs={"slug": GROUP_SLUG}
)
GROUP_2_URL = reverse(
    "group_posts",
    kwargs={"slug": GROUP_SLUG_2}
)
NEW_POST_NAME = "new_post"
POST_PAGE_NAME = "post"
USERNAME = "test_user"
USERNAME_2 = "test_user_2"
USERNAME_3 = "test_user_3"
FOLLOW_URL = reverse("profile_follow",
                     kwargs={
                         "username": USERNAME_2
                     })
UNFOLLOW_URL = reverse("profile_unfollow",
                       kwargs={
                           "username": USERNAME_2
                       })
FOLLOW_INDEX_URL_USER_1 = reverse("follow_index",
                           kwargs={
                               "username": USERNAME
                           })
FOLLOW_INDEX_URL_USER_3 = reverse("follow_index",
                           kwargs={
                               "username": USERNAME_3
                           })
SECOND_PAGE_SLUG = "?page=2"
TEST_GROUP_NAME = "test_group"
TEST_GROUP_NAME_2 = "test_group"
TEST_POST_TEXT = "This is a test post"
TEST_2_POST_TEXT = "This is a test_2 post"
NON_EXISTENT_URL = "/test_404/"
POST_WITH_IMAGE_TEXT = "post with image"
PROFILE_PAGE_URL = reverse(
    "profile",
    kwargs={
        "username": USERNAME
    }
)
ADD_COMMENT_URL_NAME = "add_comment"

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostsPagesTests(TestCase):
    """Tests the context and the templates of all the post-related pages"""
    @classmethod
    def setUpClass(cls):
        """Creation of a user, group and 2 test posts"""
        super().setUpClass()
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name="image.gif",
            content=cls.image,
            content_type="image/gif")
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.user_3 = User.objects.create_user(username="test_user_3")
        cls.group = Group.objects.create(
            title=TEST_GROUP_NAME,
            slug=GROUP_SLUG
        )
        cls.post = Post.objects.create(
            text=TEST_POST_TEXT,
            author=cls.user,
        )
        cls.post_2 = Post.objects.create(
            text=TEST_2_POST_TEXT,
            group=cls.group,
            author=cls.user,
            image=cls.uploaded
        )

    def setUp(self):
        """Creates a guest client and an authorised client
        """
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT,
                      ignore_errors=True)
        super().tearDownClass()

    def test_pages_use_correct_template(self):
        """Tests if pages use the correct template"""
        templates_pages_names = {
            INDEX_TEMPLATE: reverse(HOMEPAGE_NAME),
            NEW_POST_TEMPLATE: reverse(NEW_POST_NAME),
            GROUP_TEMPLATE: (
                reverse(GROUP_PAGE_NAME, kwargs={"slug": GROUP_SLUG})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_shows_correct_context(self):
        """Tests if the homepage shows the right context"""
        response = self.authorized_client.get(reverse(HOMEPAGE_NAME))
        first_object = response.context["page"][0]
        post_text = first_object.text
        post_author_username = first_object.author.username
        post_image = first_object.image
        self.assertEqual(post_image, PostsPagesTests.post_2.image)
        self.assertEqual(post_text, TEST_2_POST_TEXT)
        self.assertEqual(post_author_username, USERNAME)

    def test_group_page_shows_correct_context(self):
        """Tests if the group page shows the correct context"""
        response = self.authorized_client.get(GROUP_URL)
        group = response.context["group"]
        post = response.context.get("page").object_list[0]
        image = post.image
        self.assertEqual(group, PostsPagesTests.group)
        self.assertEqual(post, PostsPagesTests.post_2)
        self.assertEqual(image, PostsPagesTests.post_2.image)

    def test_new_post_page_shows_correct_context(self):
        """Tests if new post page shows correct context"""
        response = self.authorized_client.get(reverse(NEW_POST_NAME))
        form_fields = {
            "text": forms.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_group_post_is_not_on_wrong_page(self):
        """Tests if new posts don't appear on unrelated
         group pages"""
        response = self.authorized_client.get(GROUP_URL)
        number_of_posts = len(response.context["page"])
        post = response.context["page"][0]
        post_text = post.text
        self.assertEqual(number_of_posts, 1)
        self.assertEqual(post_text, TEST_2_POST_TEXT)

    def test_profile_page_correct_context_image(self):
        """Tests of if the image is passed correctly
        into the context of the profile page"""
        response = self.authorized_client.get(PROFILE_PAGE_URL)
        image_on_page = response.context["page"][0].image
        self.assertEqual(image_on_page,
                         PostsPagesTests.post_2.image)

    def test_post_page_correct_context_image(self):
        """Tests of if the image is passed correctly
        into the context of the post page"""
        post_id = self.post_2.id
        post_page_url = reverse(
            POST_PAGE_NAME,
            kwargs={
                "username": USERNAME,
                "post_id": post_id
            }
        )
        response = self.authorized_client.get(post_page_url)
        image_on_page = response.context["post"].image
        self.assertEqual(image_on_page,
                         PostsPagesTests.post_2.image)

    def test_404_page_not_found(self):
        """"Tests the 404 error handler works correctly"""
        response = self.authorized_client.get(NON_EXISTENT_URL)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "misc/404.html")

    def test_index_page_is_cached(self):
        """Tests if the index page is cached correctly"""
        response = self.authorized_client.get(HOMEPAGE_URL)
        number_of_objects_page = len(
            response.context.get("page").object_list)
        number_of_objects_database = Post.objects.all().count()
        self.assertEqual(number_of_objects_database,
                         number_of_objects_page)
        Post.objects.first().delete()
        number_of_objects_page = len(
            response.context.get("page").object_list)
        number_of_objects_database = Post.objects.all().count()
        self.assertNotEqual(number_of_objects_database,
                            number_of_objects_page)

    def test_follow_unfollow(self):
        """Test if the follow functionality works correctly"""
        self.authorized_client.get(FOLLOW_URL)
        self.assertTrue(Follow.objects.filter(
            follower=self.user,
            following=self.user_2
        ))
        self.authorized_client.get(UNFOLLOW_URL)
        self.assertFalse(Follow.objects.filter(
            follower=self.user,
            following=self.user_2
        ))

    def test_new_post_appears_on_follow_page(self):
        """Test if followers get new posts from the profiles
        they follow in the 'follow' feed. Also checks that users
        get their 'follow feed updated only  with posts from
        the people they follow"""
        self.authorized_client.get(FOLLOW_URL)
        new_post = Post.objects.create(
            text="post for follower",
            author=self.user_2
        )
        response_user1 = self.authorized_client.get(
            FOLLOW_INDEX_URL_USER_1
        )
        user1_follow_page_post = response_user1.context["page"][0]
        self.authorized_client.force_login(self.user_3)
        response_user3 = self.authorized_client.get(
            FOLLOW_INDEX_URL_USER_3
        )
        self.assertFalse(response_user3.context["page"])
        self.assertEqual(new_post, user1_follow_page_post)

    def test_only_authenticated_user_can_comment(self):
        """Tests that only authenticated users can leave comments
        for posts"""
        form_data = {
            "text": "test comment"
        }
        comment_count_initial = Comment.objects.all().count()
        response_1 = self.authorized_client.post(
            reverse(ADD_COMMENT_URL_NAME,
                    kwargs={
                        "username": USERNAME,
                        "post_id": self.post.pk
                    }),
            data=form_data,
            follow=True
        )
        comment_count_2 = Comment.objects.all().count()

        response_2 = self.guest_client.post(
            reverse(ADD_COMMENT_URL_NAME,
                    kwargs={
                        "username": USERNAME,
                        "post_id": self.post.pk
                    }),
            data=form_data,
            follow=True
        )
        comment_count_3 = Comment.objects.all().count()
        self.assertEqual(comment_count_2, comment_count_initial + 1)
        self.assertEqual(comment_count_3, comment_count_2)








class PaginatorViewsTest(TestCase):
    """Tests the correct functioning of the paginator"""
    @classmethod
    def setUpClass(cls):
        """Creates 13 posts for further testing"""
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        for x in range(13):
            Post.objects.create(
                text=f"This is a test_{x} post",
                author=cls.user
            )

    def setUp(self):
        """Client creation"""
        cache.clear()
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        """Tests if there are 10 on the first page"""
        response = self.client.get(reverse(HOMEPAGE_NAME))
        posts_on_page = len(response.context["page"])
        self.assertEqual(posts_on_page, 10)

    def test_second_page_contains_three_records(self):
        """Tests if the second page shows 3 posts"""
        response = self.client.get(reverse(HOMEPAGE_NAME) + SECOND_PAGE_SLUG)
        posts_on_page = len(response.context["page"])
        self.assertEqual(posts_on_page, 3)





