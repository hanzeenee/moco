import json
from html.parser import HTMLParser
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.structured = []
        self._json = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and "name" in attrs:
            self.meta[attrs["name"]] = attrs.get("content")
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._json = ""

    def handle_data(self, data):
        if self._json is not None:
            self._json += data

    def handle_endtag(self, tag):
        if tag == "script" and self._json is not None:
            self.structured.append(json.loads(self._json))
            self._json = None


@override_settings(DEBUG=False, SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"])
class HomePrerenderTests(SimpleTestCase):
    def page(self, locale=None, url="/"):
        if locale is None:
            self.client.cookies.pop("moconix_language", None)
        else:
            self.client.cookies["moconix_language"] = locale
        response = self.client.get(url)
        parsed = PageMetadata()
        parsed.feed(response.content.decode())
        return response, parsed

    def test_default_home_contains_visible_korean_content_without_javascript(self):
        response, _ = self.page()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html lang="ko"')
        self.assertContains(response, '<title>MOCONIX | MT5 EA·인디케이터 &amp; TradingView 지표 개발</title>')
        for text in ("원하는 매매 전략과 기능을 구현합니다", "MT5 EA·인디케이터", "TradingView 지표 맞춤 개발", "개발 의뢰", "개발 실적·후기", "무료 EA·인디케이터", "인피녹스 가입 안내", "비즈니스 제안", "EA 체험하기"):
            self.assertContains(response, text)
        self.assertContains(response, "https://open.kakao.com/o/sIPFiqUi")
        self.assertContains(response, '<h1 ', count=1)
        self.assertContains(response, 'id="app"', count=1)
        self.assertContains(response, '<v-app class="app-shell"')
        self.assertContains(response, '<v-main class="app-main"')
        self.assertNotContains(response, "v-application__wrap")
        self.assertNotContains(response, 'display:none')

    def test_english_cookie_selects_english_content_and_telegram_in_initial_html(self):
        response, parsed = self.page("en")
        self.assertContains(response, '<html lang="en"')
        self.assertContains(response, '<title>MOCONIX | Custom MT5 EAs &amp; Indicators · TradingView Indicator Development</title>')
        for text in ("We implement your trading strategies and features", "MT5 EAs &amp; Indicators", "Custom TradingView Indicators", "Development inquiry", "Get in touch on Telegram", "Free EAs &amp; Indicators"):
            self.assertContains(response, text)
        self.assertContains(response, "https://t.me/moconix")
        self.assertNotContains(response, "https://open.kakao.com/o/sIPFiqUi")
        self.assertTrue(parsed.meta["description"].startswith("Custom MT5 EA"))

    def test_unknown_cookie_uses_korean_and_responses_vary_by_cookie(self):
        response, parsed = self.page("../../en")
        self.assertContains(response, '<html lang="ko"')
        self.assertTrue(parsed.meta["description"].startswith("MT5 EA·인디케이터"))
        self.assertIn("Cookie", response.get("Vary", ""))

    def test_website_identity_is_one_valid_localized_jsonld_object(self):
        for locale in ("ko", "en"):
            with self.subTest(locale=locale):
                _, parsed = self.page(locale)
                self.assertEqual(parsed.structured, [{
                    "@context": "https://schema.org",
                    "@type": "WebSite",
                    "name": "MOCONIX",
                    "alternateName": "모코닉스",
                    "url": "https://moconix.com/",
                    "inLanguage": locale,
                }])

    def test_both_ownership_verification_tags_survive_both_locale_builds(self):
        for locale in ("ko", "en"):
            with self.subTest(locale=locale):
                _, parsed = self.page(locale)
                self.assertEqual(parsed.meta["google-site-verification"], "MFvAPMneHm0LRcfmjF7Hj-O6XYnd9Srdlib03-B9LR0")
                self.assertEqual(parsed.meta["naver-site-verification"], "aa343aa0b7319ad7f7d8267c0ec3736bd988946e")

    def test_campaign_query_keeps_localized_home_and_canonical_header(self):
        response, _ = self.page("en", "/?utm_source=youtube")
        self.assertContains(response, '<html lang="en"')
        self.assertEqual(response["Link"], '<https://moconix.com/>; rel="canonical"')

    def test_nonhome_routes_do_not_receive_public_home_snapshot_or_identity(self):
        for url in ("/lecture", "/event", "/classroom"):
            with self.subTest(url=url):
                response, parsed = self.page("en", url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(parsed.structured, [])
                self.assertNotContains(response, "intro-title")
        response, parsed = self.page("en", "/utilities")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(parsed.structured, [])
        with patch("utilities.views.registered_account", return_value=object()):
            response, parsed = self.page("en", "/utilities")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Robots-Tag"], "noindex")
        self.assertEqual(parsed.structured, [])
        self.assertNotContains(response, "intro-title")
