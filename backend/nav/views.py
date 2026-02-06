from django.shortcuts import redirect, get_object_or_404
from .models import NavLink

def go(request, key):
    link = get_object_or_404(NavLink, key=key, is_active=True)
    return redirect(link.url)
