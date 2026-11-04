import json
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .indicator_signing import _key
from .models import EAProgram, UtilityAccessAccount
from .views import ACCOUNT_KEY


@override_settings(SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"], MOCONIX_LICENSE_RATE_LIMIT=600)
class SignedIndicatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.directory = TemporaryDirectory()
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.path = Path(cls.directory.name) / "test-signing-key.pem"
        cls.path.write_bytes(cls.key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))

    @classmethod
    def tearDownClass(cls):
        _key.cache_clear()
        cls.directory.cleanup()
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.account = UtilityAccessAccount.objects.create(account_number="77112233")
        self.program = EAProgram.objects.create(code="moconix-rsi-arrow-v1", name="Example indicator", program_type="indicator")
        self.payload = {"protocol": 2, "account_number": "77112233", "server": "Example-Live", "product": self.program.code, "nonce": "AB" * 16}
        self.url = reverse("indicator-license-check")

    def post(self, payload=None, client=None, **kwargs):
        with override_settings(MOCONIX_INDICATOR_SIGNING_KEY=str(self.path)):
            return (client or self.client).post(self.url, json.dumps(self.payload if payload is None else payload), content_type="application/json", **kwargs)

    def test_signed_grant_verifies_with_public_key_and_does_not_create_browser_access(self):
        native = Client(enforce_csrf_checks=True)
        response = self.post(client=native)
        self.assertEqual(response.status_code, 200)
        message, signature = response.content.decode("ascii").split("\n")
        expected = "MOCONIX-INDICATOR-1|" + "|".join(self.payload[key] for key in ("account_number", "server", "product", "nonce"))
        self.assertEqual(message, expected)
        self.assertEqual(len(signature), 512)
        verifier = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32)
        self.key.public_key().verify(bytes.fromhex(signature), message.encode(), verifier, hashes.SHA256())
        for modified in [message + "x", message.replace("ABAB", "AAAA", 1), message.replace("77112233", "77112234")]:
            with self.assertRaises(InvalidSignature):
                self.key.public_key().verify(bytes.fromhex(signature), modified.encode(), verifier, hashes.SHA256())
        self.assertIn("no-store", response["Cache-Control"])
        self.assertFalse(response.cookies)
        self.assertNotIn(ACCOUNT_KEY, native.session)
        self.assertEqual(native.get("/utilities").status_code, 200)
        self.assertEqual(native.get(reverse("utility-library-data")).status_code, 401)

    def test_wrong_identity_flags_and_program_kind_never_receive_signature(self):
        for field, value in [("account_number", "77112234"), ("product", "unknown-indicator")]:
            self.assertEqual(self.post({**self.payload, field: value}).status_code, 403)
        for field in ["is_active", "ea_enabled"]:
            setattr(self.account, field, False)
            self.account.save()
            self.assertEqual(self.post().status_code, 403)
            setattr(self.account, field, True)
            self.account.save()
        self.program.program_type = "ea"
        self.program.save()
        self.assertEqual(self.post().status_code, 403)
        self.program.program_type = "indicator"
        self.program.is_active = False
        self.program.save()
        self.assertEqual(self.post().status_code, 403)

    def test_number_only_registration_signs_grants_for_any_valid_server(self):
        self.assertNotIn("server_name", {field.name for field in UtilityAccessAccount._meta.fields})
        verifier = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32)
        for server in ["Example-Live", "OtherBroker-Live", "Example-Demo"]:
            response = self.post({**self.payload, "server": server})
            self.assertEqual(response.status_code, 200)
            message, signature = response.content.decode("ascii").split("\n")
            self.assertEqual(message, "MOCONIX-INDICATOR-1|" + "|".join([self.account.account_number, server, self.program.code, self.payload["nonce"]]))
            self.key.public_key().verify(bytes.fromhex(signature), message.encode(), verifier, hashes.SHA256())

    def test_protocol_separation_and_transport_validation(self):
        self.assertEqual(self.post({**self.payload, "protocol": 1}).status_code, 400)
        self.assertEqual(self.client.post(reverse("ea-license-check"), json.dumps({**self.payload, "protocol": 1}), content_type="application/json").status_code, 403)
        self.assertEqual(self.post({**self.payload, "nonce": "wrong"}).status_code, 400)
        self.assertEqual(self.post(HTTP_ORIGIN="https://moconix.com").status_code, 403)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_missing_or_invalid_signer_fails_closed(self):
        for path in ["", str(self.path) + ".missing"]:
            with override_settings(MOCONIX_INDICATOR_SIGNING_KEY=path):
                response = self.client.post(self.url, json.dumps(self.payload), content_type="application/json")
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json()["protocol"], 2)
        with patch("utilities.licensing.sign_indicator_grant", side_effect=ValueError("bad configuration")):
            self.assertEqual(self.post().status_code, 503)


@override_settings(SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver"])
class PrivateDownloadTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.settings = override_settings(MOCONIX_UTILITY_DOWNLOAD_DIR=self.directory.name)
        self.settings.enable()
        self.addCleanup(self.settings.disable)
        self.account = UtilityAccessAccount.objects.create(account_number="77112233")
        self.program = EAProgram.objects.create(code="moconix-rsi-arrow-v1", name="Test indicator", program_type="indicator")
        self.path = Path(self.directory.name) / "MOCONIX_AuthBridge.ex5"
        # A private test indicator must stay unpublished even if its binary exists.
        (Path(self.directory.name) / "MOCONIX_RSIArrow.ex5").write_bytes(b"private-test-indicator")
        self.path.write_bytes(b"test-compiled-resource")
        self.url = reverse("utility-download", args=["auth-bridge"])

    def login(self):
        response = self.client.post(reverse("utility-login"), json.dumps({"account_number": self.account.account_number}), content_type="application/json")
        self.client.defaults["HTTP_X_MOCONIX_LIBRARY_TOKEN"] = response.json()["tab_token"]
        return response

    def test_anonymous_download_is_blocked_and_registered_download_is_attachment(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.login()
        items = self.client.get(reverse("utility-library-data")).json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["download_url"], self.url)
        self.assertNotIn(self.directory.name, json.dumps(items))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), self.path.read_bytes())
        self.assertIn('attachment; filename="MOCONIX_AuthBridge.ex5"', response["Content-Disposition"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_logout_account_disable_and_unpublished_indicator_protect_direct_links(self):
        self.login()
        self.client.post(reverse("utility-logout"))
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.login()
        self.account.is_active = False
        self.account.save()
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.account.is_active = True
        self.account.save()
        self.login()
        self.program.is_active = False
        self.program.save()
        # AuthBridge is shared infrastructure, independent of the private test product.
        self.program.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response.close()
        items = self.client.get(reverse("utility-library-data")).json()["items"]
        self.assertEqual([item["id"] for item in items], ["auth-bridge"])
        self.assertEqual(self.client.get(reverse("utility-download", args=["rsi-arrow"])).status_code, 404)

    def test_missing_unknown_and_source_files_are_not_exposed(self):
        self.login()
        for slug in ["missing", "rsi-arrow", "MOCONIX_RSIArrow.ex5", "MOCONIX_RSIArrow.mq5", "test-signing-key.pem"]:
            self.assertEqual(self.client.get("/api/utilities/download/" + slug + "/").status_code, 404)
        self.path.unlink()
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(self.client.get(reverse("utility-library-data")).json(), {"items": []})
