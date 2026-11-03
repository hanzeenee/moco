"""Signed, initialization-bound grants for indicators relayed by AuthBridge."""
from functools import lru_cache
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from django.conf import settings


@lru_cache(maxsize=2)
def _key(path, modified_ns):
    # The private key lives outside source/static/media and is never returned.
    data = Path(path).read_bytes()
    if len(data) > 8192:
        raise ValueError("Invalid signing key")
    key = serialization.load_pem_private_key(data, password=None)
    if not isinstance(key, rsa.RSAPrivateKey) or key.key_size != 2048 or key.public_key().public_numbers().e != 65537:
        raise ValueError("Unsupported signing key")
    return key


def sign_indicator_grant(payload):
    configured = getattr(settings, "MOCONIX_INDICATOR_SIGNING_KEY", "")
    if not configured:
        raise ValueError("Signing key is not configured")
    path = Path(configured)
    key = _key(str(path), path.stat().st_mtime_ns)
    message = "MOCONIX-INDICATOR-1|" + "|".join(payload[field] for field in ("account_number", "server", "product", "nonce"))
    signature = key.sign(message.encode("ascii"), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32), hashes.SHA256())
    return message + "\n" + signature.hex().upper()
