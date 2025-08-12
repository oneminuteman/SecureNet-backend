from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import EmailHeaderAnalysisInputSerializer, EmailHeaderAnalysisOutputSerializer
from .header_tools.header_parser import analyze_header as parse_header
from .header_tools.risk_scoring import score_risk
from .utils.parser import parse_email_header
from .utils.dns_checker import run_dns_checks
from .utils.risk_scorer import score_risk_wrapper
from .utils.classifier import classify_header_text
import logging
import re
from .models import HeaderAnalysisResult, HeaderSubmission, EmailThreatLog

logger = logging.getLogger(__name__)

def mask_sensitive(text):
    # Mask email addresses
    text = re.sub(r'([\w\.-]+)@([\w\.-]+)', r'***@\2', text)
    # Mask IPv4 addresses
    text = re.sub(r'(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})', r'***.***.***.\4', text)
    return text

@api_view(['POST'])
@swagger_auto_schema(
    request_body=EmailHeaderAnalysisInputSerializer,
    responses={200: EmailHeaderAnalysisOutputSerializer},
    operation_summary="Analyze an email header (full pipeline)",
    operation_description="Accepts a raw email header and returns a full analysis including parsing, DNS checks, risk scoring, and ML classification."
)
def analyze_email_header(request):
    """
    Accepts a raw email header and returns a full analysis.
    """
    logger.info("Received /analyze/ request", extra={"remote_addr": request.META.get("REMOTE_ADDR"), "user_agent": request.META.get("HTTP_USER_AGENT")})
    serializer = EmailHeaderAnalysisInputSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Invalid input for /analyze/", extra={"errors": serializer.errors})
        return Response({"error": "Invalid input", "details": serializer.errors}, status=400)
    raw_header = serializer.validated_data['header']
    header_preview = mask_sensitive(raw_header[:200])
    # Log the header submission
    submission = HeaderSubmission.objects.create(
        user=request.user if request.user.is_authenticated else None,
        raw_header=raw_header
    )
    logger.info("Starting analysis for /analyze/", extra={"header_preview": header_preview})
    analysis_result = parse_header(raw_header)
    risk_report = score_risk(
        analysis_result["parsed_headers"],
        analysis_result["dns_checks"],
        analysis_result["ip_info"]
    )
    analysis_result["risk_analysis"] = risk_report
    # Log a threat if risk_score is high or SPF/DKIM/DMARC fails
    if risk_report.get("risk_score", 0) >= 10 or not risk_report.get("spf", True) or not risk_report.get("dkim", True) or not risk_report.get("dmarc", True):
        EmailThreatLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            event_type="High Risk Header",
            details={"risk_score": risk_report.get("risk_score"), "reasons": risk_report.get("reasons", [])},
            related_header=submission
        )
    logger.info("Completed analysis for /analyze/", extra={"risk_score": risk_report.get("risk_score"), "reasons": risk_report.get("reasons")})
    return Response(analysis_result)

@api_view(['POST'])
@swagger_auto_schema(
    request_body=EmailHeaderAnalysisInputSerializer,
    responses={200: EmailHeaderAnalysisOutputSerializer},
    operation_summary="Enhanced header analysis with ML classification",
    operation_description="Enhanced header analysis endpoint with ML classification. Returns parsed fields, DNS, risk, ML label, and geolocation."
)
def analyze_header(request):
    """
    Enhanced header analysis endpoint with ML classification.
    """
    logger.info("Received /analyze-header/ request", extra={"remote_addr": request.META.get("REMOTE_ADDR"), "user_agent": request.META.get("HTTP_USER_AGENT")})
    serializer = EmailHeaderAnalysisInputSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning("Invalid input for /analyze-header/", extra={"errors": serializer.errors})
        return Response({"error": "Invalid input", "details": serializer.errors}, status=400)
    raw_header = serializer.validated_data["header"]
    header_preview = mask_sensitive(raw_header[:200])
    # Log the header submission
    submission = HeaderSubmission.objects.create(
        user=request.user if request.user.is_authenticated else None,
        raw_header=raw_header
    )
    logger.info("Starting analysis for /analyze-header/", extra={"header_preview": header_preview})
    try:
        parsed = parse_email_header(raw_header)
        # The parsed data already contains the DNS information in spf_dkim_dmarc_records
        # and delivery_info, so we don't need to run separate DNS checks
        risk = score_risk_wrapper(parsed, {})  # DNS info is extracted from parsed in the wrapper
        ml_result = classify_header_text(raw_header)
        # Always provide a meaningful classification and confidence
        classification = ml_result.get('label', '').strip().lower()
        if not classification or classification == 'unknown':
            classification = 'analysis results'
        # Confidence is proportional to risk_score (max 5)
        risk_score_val = risk.get('risk_score', 0)
        confidence = ml_result.get('confidence', None)
        if confidence is None or confidence == 0:
            confidence = min(1, risk_score_val / 5) if risk_score_val > 0 else 0.5
        logger.info("Completed analysis for /analyze-header/", extra={
            "risk_score": risk_score_val,
            "ml_label": classification,
            "confidence": confidence,
            "reasons": risk.get("reasons")
        })
        # The frontend expects the data structure from analyze_header directly
        result_data = parsed
        # Flatten the structure to match frontend expectations
        if "parsed_headers" in result_data and "summary" in result_data["parsed_headers"]:
            result_data["summary"] = result_data["parsed_headers"]["summary"]
        # Add ML classification results
        result_data["classification"] = classification
        result_data["confidence"] = confidence
        result_data["risk_score"] = risk_score_val
        result_data["reasons"] = risk.get("reasons", [])
        # Store analysis only if user is authenticated
        if request.user.is_authenticated:
            HeaderAnalysisResult.objects.create(
                user=request.user,
                raw_header=raw_header,
                result_json=result_data,
                client_ip=request.META.get("REMOTE_ADDR")
            )
        # Log a threat if risk_score is high or SPF/DKIM/DMARC fails
        # Extract DNS info from parsed data for threat logging
        delivery_info = parsed.get("delivery_info", {})
        if risk.get("risk_score", 0) >= 10 or not delivery_info.get("spf", {}).get("published", True) or not delivery_info.get("dkim", {}).get("published", True) or not delivery_info.get("dmarc", {}).get("compliant", True):
            EmailThreatLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                event_type="High Risk Header",
                details={"risk_score": risk.get("risk_score"), "reasons": risk.get("reasons", [])},
                related_header=submission
            )
        return Response(result_data)
    except Exception as e:
        logger.error("Critical error in /analyze-header/", exc_info=True, extra={"header_preview": header_preview})
        return Response({
            "error": f"Analysis failed: {str(e)}"
        }, status=500)
