import json
import re
import time

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import UtilityAccessAccount

ACCOUNT_KEY = "utility_account_id"
EXPIRY_KEY = "utility_access_expires_at"
ACCESS_SECONDS = 8 * 60 * 60


def clear_access(request):
    # Keep the independent Django administrator login/session intact.
    request.session.pop(ACCOUNT_KEY, None)
    request.session.pop(EXPIRY_KEY, None)


def registered_account(request):
    account_id = request.session.get(ACCOUNT_KEY)
    expires = request.session.get(EXPIRY_KEY)
    if not isinstance(account_id, int) or not isinstance(expires, (int, float)) or expires <= time.time():
        clear_access(request)
        return None
    account = UtilityAccessAccount.objects.filter(pk=account_id, is_active=True).first()
    if account is None:
        clear_access(request)
    return account


@never_cache
@ensure_csrf_cookie
@require_GET
def session_status(request):
    return JsonResponse({"authenticated": registered_account(request) is not None})


@never_cache
@require_POST
def login(request):
    clear_access(request)
    if request.content_type != "application/json":
        return JsonResponse({"detail": "올바른 요청 형식이 아닙니다."}, status=415)
    if len(request.body) > 256:
        return JsonResponse({"detail": "입력 내용을 확인해 주세요."}, status=400)
    try:
        payload = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        payload = None
    value = payload.get("account_number") if isinstance(payload, dict) else None
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,20}", value.strip()):
        return JsonResponse({"detail": "인피녹스 계좌번호를 숫자로 입력해 주세요."}, status=400)
    account = UtilityAccessAccount.objects.filter(account_number=value.strip(), is_active=True).first()
    if account is None:
        return JsonResponse({"detail": "등록되지 않았거나 이용이 중지된 계좌번호입니다."}, status=403)
    request.session.cycle_key()
    request.session[ACCOUNT_KEY] = account.pk
    request.session[EXPIRY_KEY] = time.time() + ACCESS_SECONDS
    return JsonResponse({"authenticated": True})


@never_cache
@require_POST
def logout(request):
    clear_access(request)
    return JsonResponse({"authenticated": False})


@never_cache
@require_GET
def library_data(request):
    if registered_account(request) is None:
        return JsonResponse({"detail": "자료실 로그인이 필요합니다."}, status=401)
    # No files yet. Future file-list and download endpoints must use the same guard.
    return JsonResponse({"items": []})


@never_cache
@ensure_csrf_cookie
@require_GET
def library_page(request):
    if registered_account(request) is None:
        return render(request, "utilities/access_required.html", status=403)
    return render(request, "home.html")
