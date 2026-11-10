from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe


@require_safe
def robots_txt(request):
    return HttpResponse(
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /api/\n"
        "\n"
        "Sitemap: https://moconix.com/sitemap.xml\n",
        content_type="text/plain; charset=utf-8",
    )


@require_safe
def sitemap_xml(request):
    # Only the public home page is intended for search. Legacy views and the
    # account-protected library remain available through their existing routes.
    return HttpResponse(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url><loc>https://moconix.com/</loc></url>\n'
        '</urlset>\n',
        content_type="application/xml; charset=utf-8",
    )


def page_not_found(request, exception):
    english = request.COOKIES.get("moconix_language") == "en"
    response = render(request, "404.html", {"english": english}, status=404)
    response["X-Robots-Tag"] = "noindex"
    return response
