import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

HOME_PAGE = reverse("index")
NEW_POST_URL = reverse("new_post")

USERNAME = "test_user"
GROUP_SLUG = "test_group"

TEST_GROUP_TITLE = "test_group"
TEST_POST_TEXT = "test post"
TEST_POST_CREATE_TEXT = "test create post"
TEST_POST_EDIT_TEXT = "test edit post"
IMG_POST = "post with image"
MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostFormTest(TestCase):
    """Tests the for for new post creation"""
    @classmethod
    def setUpClass(cls):
        """Creation of a test user, group and post"""
        super().setUpClass()
        img = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='image.gif',
            content=img,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(
            username=USERNAME
        )
        cls.group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            slug=GROUP_SLUG
        )
        cls.post_with_img = Post.objects.create(
            text=IMG_POST,
            author=PostFormTest.user,
            group=PostFormTest.group,
            image=cls.uploaded
        )
        cls.post = Post.objects.create(
            text=TEST_POST_TEXT,
            author=cls.user,
            group=cls.group,
        )
        cls.post_id = cls.post.id
        cls.post_edit_url = reverse(
            "post_edit",
            kwargs={
                "username": USERNAME,
                "post_id": cls.post_id
            })
        cls.form = PostForm()

    def setUp(self):
        """Creation of an authorised client"""
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT,
                      ignore_errors=True)
        super().tearDownClass()

    def test_edit_post(self):
        """Test if posts can be successfully edited"""
        form_data = {
            "text": TEST_POST_EDIT_TEXT,
            "group": self.group.pk
        }
        self.authorised_client.post(
            self.post_edit_url,
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.first()
        posts_compare = {
            edited_post.id: self.post_id,
            edited_post.group: self.group,
            edited_post.text: TEST_POST_EDIT_TEXT,
            edited_post.author: self.user
        }
        for value, expected in posts_compare.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_create_post(self):
        """Tests if the post is saved into the
         database after creation and if the
         client is redirected to the homepage """
        last_post_created = Post.objects.first()
        last_post_id = last_post_created.id
        post_count = Post.objects.count()
        form_data = {
            "text": TEST_POST_CREATE_TEXT,
            "group": self.group.pk,
        }
        response = self.authorised_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )

        new_post_created = Post.objects.first()

        self.assertRedirects(response, HOME_PAGE)
        self.assertTrue(new_post_created.id != last_post_id)

        posts_compare = {
            Post.objects.count(): post_count + 1,
            new_post_created.text: TEST_POST_CREATE_TEXT,
            new_post_created.group: self.group,
        }
        for value, expected in posts_compare.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_post_with_image(self):
        """Tests if post with image is saved to database
        and if it's passed correctly to the context for the pages
        index, group, profile and post"""
        image = self.post_with_img.image
        image_in_database = Post.objects.last().image
        self.assertEqual(image_in_database, image)

