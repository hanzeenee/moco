import hashlib
import json
import re
import secrets

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import UtilityAccessAccount, UtilityBrowserSession
from .resources import available_resources, resource_path

# Legacy utility keys are removed on login/logout, never accepted for access.
ACCOUNT_KEY = "utility_account_id"
EXPIRY_KEY = "utility_access_expires_at"
COOKIE_NAME = "moconix_library_session"


def token_digest(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", value):
        return None
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def clear_access(request):
    digest = token_digest(request.COOKIES.get(COOKIE_NAME))
    if digest is not None:
        UtilityBrowserSession.objects.filter(token_hash=digest).delete()
    # Keep the independent Django administrator login and its expiry intact.
    request.session.pop(ACCOUNT_KEY, None)
    request.session.pop(EXPIRY_KEY, None)
    request._utility_clear_cookie = True


def access_response(request, response):
    if getattr(request, "_utility_clear_cookie", False):
        response.delete_cookie(COOKIE_NAME, path="/", samesite="Lax")
        response.cookies[COOKIE_NAME]["secure"] = settings.SESSION_COOKIE_SECURE
        response.cookies[COOKIE_NAME]["httponly"] = True
    return response


def registered_account(request):
    token = request.COOKIES.get(COOKIE_NAME)
    digest = token_digest(token)
    if digest is None:
        if token is not None:
            request._utility_clear_cookie = True
        return None
    grant = UtilityBrowserSession.objects.select_related("account").filter(token_hash=digest).first()
    if grant is None:
        request._utility_clear_cookie = True
        return None
    if not grant.account.is_active:
        grant.delete()
        request._utility_clear_cookie = True
        return None
    return grant.account


@never_cache
@ensure_csrf_cookie
@require_GET
def session_status(request):
    return access_response(request, JsonResponse({"authenticated": registered_account(request) is not None}))


@never_cache
@require_POST
def login(request):
    clear_access(request)
    if request.content_type != "application/json":
        return access_response(request, JsonResponse({"detail": "올바른 요청 형식이 아닙니다."}, status=415))
    if len(request.body) > 256:
        return access_response(request, JsonResponse({"detail": "입력 내용을 확인해 주세요."}, status=400))
    try:
        payload = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        payload = None
    value = payload.get("account_number") if isinstance(payload, dict) else None
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,20}", value.strip()):
        return access_response(request, JsonResponse({"detail": "인피녹스 계좌번호를 숫자로 입력해 주세요."}, status=400))
    account = UtilityAccessAccount.objects.filter(account_number=value.strip(), is_active=True).first()
    if account is None:
        return access_response(request, JsonResponse({"detail": "등록되지 않았거나 이용이 중지된 계좌번호입니다."}, status=403))
    token = secrets.token_urlsafe(32)
    UtilityBrowserSession.objects.create(token_hash=token_digest(token), account=account)
    response = JsonResponse({"authenticated": True})
    # No expiry attributes: the browser owns this cookie's session lifetime.
    response.set_cookie(
        COOKIE_NAME, token, path="/", secure=settings.SESSION_COOKIE_SECURE,
        httponly=True, samesite="Lax",
    )
    request._utility_clear_cookie = False
    return response


@never_cache
@require_POST
def logout(request):
    clear_access(request)
    return access_response(request, JsonResponse({"authenticated": False}))


@never_cache
@require_GET
def library_data(request):
    if registered_account(request) is None:
        return access_response(request, JsonResponse({"detail": "자료실 로그인이 필요합니다."}, status=401))
    return access_response(request, JsonResponse({"items": available_resources()}))


@never_cache
@ensure_csrf_cookie
@require_GET
def library_page(request):
    if registered_account(request) is None:
        language = "en" if request.COOKIES.get("moconix_language") == "en" else "ko"
        response = render(request, "utilities/access_required.html", {"english": language == "en", "language": language}, status=403)
    else:
        response = render(request, "home.html")
    response["X-Robots-Tag"] = "noindex"
    return access_response(request, response)


@never_cache
@require_GET
def download(request, resource_id):
    if registered_account(request) is None:
        return access_response(request, JsonResponse({"detail": "자료실 로그인이 필요합니다."}, status=401))
    path = resource_path(resource_id)
    if path is None:
        raise Http404()
    response = FileResponse(path.open("rb"), as_attachment=True, filename=path.name, content_type="application/octet-stream")
    response["X-Content-Type-Options"] = "nosniff"
    return response
