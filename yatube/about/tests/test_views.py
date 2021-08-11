from django.test import Client, TestCase
from django.urls import reverse

AUTHOR_TEMPLATE = "about/author.html"
AUTHOR_URL = reverse("about:author")
TECH_TEMPLATE = "about/tech.html"
TECH_URL = reverse("about:tech")


class AboutAndTechPagesTest(TestCase):
    """Tests if About author and Technologies pages work
    correctly"""
    def SetUp(self):
        self.client = Client()

    def test_pages_uses_correct_context(self):
        """Tests if correct templates are used
        for about author and tech pages"""
        templates_pages_names = {
            AUTHOR_TEMPLATE: AUTHOR_URL,
            TECH_TEMPLATE: TECH_URL
        }
        for template, url in templates_pages_names.items():
            with self.subTest(reverse_name=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
