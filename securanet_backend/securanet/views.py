import os
from urllib.parse import urlparse
from django.http import JsonResponse, HttpResponse
from django.core.files import File
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .utils.crawler import capture_site
from .utils.compare import get_html_signature, html_similarity
from .utils.detector import detect_clone
from .utils.domain_check import get_domain_reputation
from .models import SuspiciousSite, ScanLog


# ✅ 1. Health check route
def home_view(request):
    return HttpResponse("<h2>✅ SecureNet Clone Site Detection is running!</h2>")


# ✅ 2. Capture a screenshot of a given URL
def capture_view(request):
    url = request.GET.get("url")
    if not url:
        return JsonResponse({"error": "URL parameter missing"}, status=400)

    screenshot_path = capture_site(url)

    if screenshot_path:
        return JsonResponse({
            "status": "success",
            "screenshot": screenshot_path,
            "screenshot_url": request.build_absolute_uri(
                settings.MEDIA_URL + "screenshots/" + os.path.basename(screenshot_path)
            )
        })
    else:
        return JsonResponse({
            "status": "failed",
            "message": "Unable to capture screenshot"
        })


# ✅ 3. Compare HTML structure of two URLs
def compare_sites_view(request):
    url1 = request.GET.get("url1")
    url2 = request.GET.get("url2")

    if not url1 or not url2:
        return JsonResponse({"error": "Missing url1 or url2"}, status=400)

    html1 = get_html_signature(url1)
    html2 = get_html_signature(url2)

    if html1 and html2:
        score = html_similarity(html1, html2)
        return JsonResponse({"similarity_score": round(score, 3)})
    else:
        return JsonResponse({"error": "Failed to retrieve HTML for one or both sites"}, status=500)


# ✅ 4. Detect site and return result
def detect_view(request):
    url = request.GET.get("url")
    if not url:
        return JsonResponse({"error": "Missing URL"}, status=400)

    result = detect_clone(url)
    domain = urlparse(url).netloc
    detection_method = result.get("method", "unknown")
    screenshot_path = result.get("screenshot")

    # Store full screenshot URL if available
    if screenshot_path:
        full_path = os.path.join(settings.MEDIA_ROOT, screenshot_path)
        if os.path.exists(full_path):
            result["screenshot_url"] = request.build_absolute_uri(
                settings.MEDIA_URL + screenshot_path
            )

    # ✅ Save result to ScanLog
    ScanLog.objects.create(
        url=url,
        domain=domain,
        status=result.get("status"),
        method=detection_method,
        reason=result.get("reason"),
        reputation=result.get("reputation"),
        google_safebrowsing=result.get("google_safebrowsing"),
        virustotal=result.get("virustotal"),
        message=result.get("message"),
        screenshot=result.get("screenshot")
    )

    # ✅ Save to SuspiciousSite only if flagged
    if result.get("status") == "flagged":
        if screenshot_path and os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                screenshot_file = File(f, name=os.path.basename(screenshot_path))
                SuspiciousSite.objects.create(
                    url=url,
                    domain=domain,
                    is_flagged=True,
                    reason=result.get("reason"),
                    screenshot=screenshot_file,
                    detection_method=detection_method
                )
        else:
            SuspiciousSite.objects.create(
                url=url,
                domain=domain,
                is_flagged=True,
                reason=result.get("reason"),
                detection_method=detection_method
            )

    return JsonResponse(result)


# ✅ 5. Recent scans API (for frontend)
@csrf_exempt
def recent_scans(request):
    logs = ScanLog.objects.order_by('-created_at')[:10]
    return JsonResponse([
        {
            "status": log.status,
            "reason": log.reason,
            "method": log.method,
            "reputation": log.reputation,
            "google_safebrowsing": log.google_safebrowsing,
            "virustotal": log.virustotal,
            "message": log.message,
            "screenshot": log.screenshot,
            "url": log.url,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ], safe=False)


# ✅ 6. Test WhoisXML reputation API manually
def test_whoisxml(request):
    domain = request.GET.get("domain", "example.com")
    rep = get_domain_reputation(domain)
    return JsonResponse({"domain": domain, "reputation": rep})

