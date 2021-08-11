from django.test import Client, TestCase
from django.urls import reverse

AUTHOR_URL = reverse("about:author")
TECH_URL = reverse("about:tech")


class UrlsAboutAndTechTest(TestCase):
    """Tests the urls of about and technologies used pages"""
    def setUp(self):
        self.client = Client()

    def test_pages_show_at_correct_urls(self):
        """Checks if we get the expected status code from
        about author and technologies used pages"""
        response_author = self.client.get(AUTHOR_URL)
        response_tech = self.client.get(TECH_URL)
        self.assertEqual(response_tech.status_code, 200)
        self.assertEqual(response_author.status_code, 200)
