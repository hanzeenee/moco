"""Session-independent, one-time MT5 startup authorization (protocol 1)."""
import hashlib
import ipaddress
import json
import re
import time

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from .indicator_signing import sign_indicator_grant
from .models import EAProgram, PROGRAM_PATTERN, SERVER_PATTERN, UtilityAccessAccount

MAX_BODY_BYTES = 1024
MAX_ACCOUNT_NUMBER = 9223372036854775807
REQUEST_FIELDS = {"protocol", "account_number", "server", "product", "nonce"}


def _response(data, status=200):
    # Protocol 1 has a canonical field order/encoding, compared in full by MT5.
    response = JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": True, "separators": (",", ":")})
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _denied(code="not_authorized", status=403, protocol=1):
    return _response({"protocol": protocol, "allowed": False, "error": code}, status)


def _client_ip(request):
    # Production nginx overwrites X-Real-IP and reaches gunicorn on loopback.
    remote = request.META.get("REMOTE_ADDR", "")
    try:
        address = ipaddress.ip_address(remote)
        forwarded = request.META.get("HTTP_X_REAL_IP", "")
        if address.is_loopback and forwarded:
            return str(ipaddress.ip_address(forwarded))
        return str(address)
    except ValueError:
        return "unknown"


def _rate_limited(request):
    # Best-effort per-worker protection with the default local-memory cache.
    limit = max(1, int(getattr(settings, "MOCONIX_LICENSE_RATE_LIMIT", 600)))
    identity = hashlib.sha256(_client_ip(request).encode()).hexdigest()
    key = f"moconix-license-v1:{int(time.time()) // 60}:{identity}"
    if cache.add(key, 1, timeout=65):
        return False
    try:
        return cache.incr(key) > limit
    except ValueError:
        cache.add(key, 1, timeout=65)
        return False


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def valid_account(value):
    return (isinstance(value, str) and re.fullmatch(r"[1-9][0-9]{0,18}", value) is not None
            and int(value) <= MAX_ACCOUNT_NUMBER)


def _license_payload(request, protocol):
    def deny(code="not_authorized", status=403):
        return _denied(code, status, protocol)
    if request.method != "POST":
        response = deny("method_not_allowed", 405)
        response["Allow"] = "POST"
        return None, response
    if request.META.get("HTTP_ORIGIN"):
        return None, deny()
    try:
        if _rate_limited(request):
            response = deny("rate_limited", 429)
            response["Retry-After"] = "60"
            return None, response
    except Exception:
        # Infrastructure failure cannot turn into a successful authorization.
        return None, deny("temporarily_unavailable", 503)
    if request.content_type != "application/json":
        return None, deny("invalid_request", 415)
    try:
        size = int(request.META.get("CONTENT_LENGTH") or 0)
    except ValueError:
        return None, deny("invalid_request", 400)
    if size > MAX_BODY_BYTES:
        return None, deny("invalid_request", 413)
    body = request.body
    if len(body) > MAX_BODY_BYTES:
        return None, deny("invalid_request", 413)
    try:
        payload = json.loads(body.decode("utf-8"), object_pairs_hook=_unique_object)
    except (ValueError, UnicodeDecodeError):
        return None, deny("invalid_request", 400)
    if not isinstance(payload, dict) or set(payload) != REQUEST_FIELDS:
        return None, deny("invalid_request", 400)
    number, server, product, nonce = (payload[key] for key in ("account_number", "server", "product", "nonce"))
    if (type(payload["protocol"]) is not int or payload["protocol"] != protocol
            or not valid_account(number)
            or not isinstance(server, str) or re.fullmatch(SERVER_PATTERN, server) is None
            or not isinstance(product, str) or re.fullmatch(PROGRAM_PATTERN, product) is None
            or not isinstance(nonce, str) or re.fullmatch(r"[a-fA-F0-9]{32}", nonce) is None):
        return None, deny("invalid_request", 400)
    return payload, None


def _authorized(payload, program_type):
    return (EAProgram.objects.filter(code=payload["product"], program_type=program_type, is_active=True).exists()
            and UtilityAccessAccount.objects.filter(account_number=payload["account_number"],
                server_name=payload["server"], is_active=True, ea_enabled=True).exists())


@csrf_exempt  # Native MT5 has no browser session authority.
@never_cache
def check_license(request):
    payload, error = _license_payload(request, 1)
    if error is not None:
        return error
    if not _authorized(payload, "ea"):
        return _denied()
    return _response({"protocol": 1, "allowed": True, **{key: payload[key] for key in ("account_number", "server", "product", "nonce")}})


@csrf_exempt  # Separate signed native endpoint; grants no website session.
@never_cache
def check_indicator_license(request):
    payload, error = _license_payload(request, 2)
    if error is not None:
        return error
    if not _authorized(payload, "indicator"):
        return _denied(protocol=2)
    try:
        grant = sign_indicator_grant(payload)
    except (OSError, ValueError, TypeError):
        return _denied("temporarily_unavailable", 503, protocol=2)
    response = HttpResponse(grant, content_type="text/plain; charset=us-ascii")
    response["X-Content-Type-Options"] = "nosniff"
    return response
