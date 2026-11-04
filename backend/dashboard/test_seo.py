from xml.etree import ElementTree

from django.test import SimpleTestCase, override_settings
from django.urls import resolve

from dashboard import views as dashboard_views
from utilities import views as utility_views
from utilities.licensing import check_indicator_license, check_license


@override_settings(DEBUG=False, SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"])
class PublicSeoTests(SimpleTestCase):
    def test_robots_is_text_and_keeps_public_assets_crawlable(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/plain"))
        text = response.content.decode()
        for line in ("User-agent: *", "Disallow: /admin/", "Disallow: /api/", "Disallow: /utilities", "Sitemap: https://moconix.com/sitemap.xml"):
            self.assertIn(line, text)
        self.assertNotIn("Disallow: /static", text)
        self.assertNotIn("<!doctype", text.lower())

    def test_sitemap_only_lists_the_public_canonical_homepage(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/xml"))
        root = ElementTree.fromstring(response.content)
        self.assertEqual(root.tag, "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")
        locations = root.findall("{*}url/{*}loc")
        self.assertEqual([item.text for item in locations], ["https://moconix.com/"])
        self.assertEqual(self.client.head("/sitemap.xml").status_code, 200)
        self.assertEqual(self.client.head("/robots.txt").status_code, 200)

    def test_existing_public_vue_routes_still_render_the_app(self):
        for url in ("/", "/lecture", "/lecture/", "/event", "/event/", "/classroom", "/classroom/"):
            with self.subTest(url=url):
                self.assertEqual(resolve(url).func, dashboard_views.dashboard_home)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'id="app"')

    def test_legacy_pages_remain_accessible_but_noindex_for_both_languages(self):
        for locale in ("ko", "en"):
            self.client.cookies["moconix_language"] = locale
            for path in ("/lecture", "/event", "/classroom"):
                for trailing in ("", "/"):
                    for query in ("", "?utm_source=shared-link"):
                        url = path + trailing + query
                        for method in ("get", "head"):
                            with self.subTest(locale=locale, url=url, method=method):
                                response = getattr(self.client, method)(url)
                                self.assertEqual(response.status_code, 200)
                                self.assertEqual(response["X-Robots-Tag"], "noindex")
                                self.assertNotIn("Link", response)
                                if method == "get":
                                    self.assertContains(response, 'id="app"')
                                else:
                                    self.assertEqual(response.content, b"")

    def test_home_remains_indexable_for_both_languages_and_request_methods(self):
        for locale in ("ko", "en"):
            self.client.cookies["moconix_language"] = locale
            for url in ("/", "/?utm_source=youtube"):
                for method in ("get", "head"):
                    with self.subTest(locale=locale, url=url, method=method):
                        response = getattr(self.client, method)(url)
                        self.assertEqual(response.status_code, 200)
                        self.assertNotIn("X-Robots-Tag", response)
                        self.assertEqual(response["Link"], '<https://moconix.com/>; rel="canonical"')

    def test_unused_dashboard_api_is_retired_without_removing_comments(self):
        for method in ("get", "head"):
            with self.subTest(method=method):
                response = getattr(self.client, method)("/api/dashboard/?source=old-client")
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response["X-Robots-Tag"], "noindex")
        self.assertEqual(resolve("/api/comments/").func, dashboard_views.comments_api)
        for method in ("get", "post"):
            for payload, detail in (({}, "lecture_id is required."), ({"lecture_id": "invalid"}, "lecture_id must be an integer.")):
                with self.subTest(method=method, payload=payload):
                    response = getattr(self.client, method)("/api/comments/", payload)
                    self.assertEqual(response.status_code, 400)
                    self.assertEqual(response.json(), {"detail": detail})

    def test_unknown_and_reserved_paths_are_real_404_responses(self):
        for url in ("/seo-missing-page", "/lecture/missing", "/api/seo-missing", "/accounts/login/", "/static/seo-missing", "/media/seo-missing"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response["X-Robots-Tag"], "noindex")
                self.assertContains(response, "페이지를 찾을 수 없습니다", status_code=404)
                self.assertNotContains(response, 'id="app"', status_code=404)

    def test_404_uses_existing_language_preference(self):
        self.client.cookies["moconix_language"] = "en"
        response = self.client.get("/seo-missing-page")
        self.assertContains(response, 'lang="en"', status_code=404)
        self.assertContains(response, "Page not found", status_code=404)
        self.assertContains(response, 'href="/"', status_code=404)

    def test_library_and_license_routes_keep_their_original_handlers(self):
        for url in ("/utilities", "/utilities/"):
            self.assertEqual(resolve(url).func, utility_views.library_page)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["X-Robots-Tag"], "noindex")
            self.assertContains(response, 'id="app"')
            self.assertNotContains(response, 'download_url')
        self.assertEqual(resolve("/api/licenses/check/").func, check_license)
        self.assertEqual(resolve("/api/licenses/indicator/").func, check_indicator_license)
        self.assertEqual(self.client.get("/api/utilities/library/").status_code, 401)

    def test_canonical_header_only_applies_to_home_including_query_urls(self):
        for url in ("/", "/?utm_source=youtube"):
            self.assertEqual(self.client.get(url)["Link"], '<https://moconix.com/>; rel="canonical"')
        for url in ("/lecture", "/event/", "/classroom", "/robots.txt", "/sitemap.xml", "/utilities"):
            self.assertNotIn("Link", self.client.get(url))

    def test_library_bootstrap_is_noindex_without_exposing_protected_data(self):
        for url in ("/utilities", "/utilities/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["X-Robots-Tag"], "noindex")
            self.assertIn("no-store", response["Cache-Control"])
            self.assertContains(response, 'id="app"')
            self.assertNotContains(response, 'download_url')
            self.assertNotContains(response, 'account_number')
            self.assertNotContains(response, 'resource-card')
            self.assertNotIn("Link", response)
