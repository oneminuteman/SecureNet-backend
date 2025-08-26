from rest_framework import serializers

class EmailHeaderAnalysisInputSerializer(serializers.Serializer):
    header = serializers.CharField(help_text="Raw email header text to analyze.")

class EmailHeaderSummarySerializer(serializers.Serializer):
    from_ = serializers.DictField(source='from', help_text="Sender information (name, email)")
    sender_ip = serializers.CharField(allow_blank=True, required=False)
    subject = serializers.CharField(allow_blank=True, required=False)

class EmailHeaderRoutingHopSerializer(serializers.Serializer):
    from_ = serializers.CharField(source='from', allow_blank=True, required=False)
    by = serializers.CharField(allow_blank=True, required=False)
    timestamp = serializers.CharField(allow_blank=True, required=False)
    from_ip = serializers.CharField(allow_blank=True, required=False)
    raw = serializers.CharField(allow_blank=True, required=False)
    error = serializers.CharField(allow_blank=True, required=False)

class EmailHeaderAnalysisOutputSerializer(serializers.Serializer):
    parsed = serializers.DictField(help_text="Parsed header fields (summary, authentication, routing, dkim_signature, return_path)")
    dns = serializers.DictField(help_text="DNS check results (SPF, DKIM, DMARC)")
    risk_score = serializers.IntegerField(help_text="Calculated risk score")
    reasons = serializers.ListField(child=serializers.CharField(), help_text="Reasons for risk score")
    classification = serializers.CharField(help_text="ML classification label")
    confidence = serializers.FloatField(help_text="ML classification confidence")
    ip_info = serializers.DictField(help_text="IP geolocation information")
    error = serializers.CharField(required=False, help_text="Error message if analysis failed") 