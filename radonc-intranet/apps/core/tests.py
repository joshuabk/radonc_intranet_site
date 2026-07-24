from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


class SmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("bootstrap_site")
        call_command("seed_demo")
        cls.user = User.objects.create_user("tester", password="pw", first_name="Test")
        cls.reporter = User.objects.create_user("reporter", password="pw")
        cls.reporter.groups.add(Group.objects.get(name=settings.SITE_GROUPS["REPORTING"]))

    def test_login_required_everywhere(self):
        for name in ["core:home", "linkhub:hub", "contacts:list",
                     "coverage:home", "coverage:matrix", "huddle:board"]:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 302, name)
            self.assertIn("/accounts/login/", resp.url)

    def test_pages_render_for_signed_in_staff(self):
        self.client.login(username="tester", password="pw")
        for name in ["core:home", "linkhub:hub", "contacts:list",
                     "coverage:home", "coverage:matrix", "huddle:board"]:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 200, name)

    def test_reporting_requires_group(self):
        self.client.login(username="tester", password="pw")
        resp = self.client.get(reverse("reporting:list"))
        self.assertEqual(resp.status_code, 302)  # bounced to login_url

        self.client.login(username="reporter", password="pw")
        resp = self.client.get(reverse("reporting:list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ARIA")

    def test_reporting_feature_hidden_from_non_members(self):
        self.client.login(username="tester", password="pw")
        resp = self.client.get(reverse("core:home"))
        self.assertNotContains(resp, reverse("reporting:list"))

    def test_search(self):
        self.client.login(username="tester", password="pw")
        resp = self.client.get(reverse("core:search"), {"q": "ARIA"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ARIA")

    def test_coverage_matrix_location_filter(self):
        self.client.login(username="tester", password="pw")
        resp = self.client.get(reverse("coverage:matrix"), {"location": "1"})
        self.assertEqual(resp.status_code, 200)


class DatasourceTests(TestCase):
    def test_unconfigured_source_raises_friendly_error(self):
        from apps.reporting.datasources import (DataSourceNotConfigured,
                                                run_readonly_query)
        with self.assertRaises(DataSourceNotConfigured):
            run_readonly_query("aria", "SELECT 1")

    def test_non_select_rejected(self):
        from apps.reporting.datasources import run_readonly_query
        with self.assertRaises(ValueError):
            run_readonly_query("default", "DELETE FROM x")
