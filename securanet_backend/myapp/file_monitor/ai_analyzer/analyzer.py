from typing import List, Dict

class SecurityAnalyzer:
    def __init__(self):
        self.dangerous_patterns = {
            'command_injection': [
                r'os\.system\(',
                r'subprocess\.(call|Popen|getoutput)\(',
                r'exec\(',
                r'eval\(',
                r'shell\s*=\s*True',
                r'commands\.getoutput\(',
                r'popen\('
            ],
            'hardcoded_credentials': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret[\w_]*\s*=\s*["\'][^"\']+["\']',
                r'api[_]?key\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'credentials\s*=\s*["\'][^"\']+["\']',
                r'auth[\w_]*\s*=\s*["\'][^"\']+["\']'
            ],
            'unsafe_network': [
                r'socket\.socket\(',
                r'bind\(["\']0\.0\.0\.0["\']',
                r'listen\(',
                r'requests\.',
                r'urllib\.',
                r'ftp\.',
                r'telnet\.'
            ],
            'file_operations': [
                r'open\([^)]+,\s*["\']w["\']',
                r'write\(',
                r'writelines\(',
                r'shutil\.(copy|move|rmtree)',
                r'os\.(remove|unlink|rmdir)'
            ],
            'crypto_concerns': [
                r'md5',
                r'sha1',
                r'random\.',
                r'hashlib\.md5',
                r'hashlib\.sha1'
            ]
        }

    def _get_severity_multiplier(self, category: str) -> float:
        multiplier_map = {
            'command_injection': 3.0,     # Increased from 2.0
            'hardcoded_credentials': 2.0,  # Increased from 1.5
            'unsafe_network': 1.5,        # Increased from 1.0
            'file_operations': 0.8,       # Increased from 0.5
            'crypto_concerns': 1.2        # New category
        }
        return multiplier_map.get(category, 0.5)

    def _determine_risk_level(self, risk_score: float) -> str:
        if risk_score >= 80:  # Lowered from 70
            return 'dangerous'
        elif risk_score >= 40:  # Increased from 30
            return 'suspicious'
        return 'safe'

    def _generate_recommendation(self, threats: List[Dict], risk_level: str) -> str:
        if not threats:
            return "No security concerns detected. The file appears to be safe."

        recommendations = []
        for threat in threats:
            category = threat['category']
            severity = threat['severity']
            count = len(threat['instances'])
            
            if category == 'command_injection':
                recommendations.append(
                    f"CRITICAL: Found {count} instances of potential command injection. "
                    "Replace os.system/exec calls with subprocess.run with proper argument escaping. "
                    "Always validate and sanitize input before execution."
                )
            elif category == 'hardcoded_credentials':
                recommendations.append(
                    f"HIGH RISK: Detected {count} hardcoded credentials. "
                    "Move sensitive data to environment variables or secure secret storage. "
                    "Consider using a secure secrets management system."
                )
            elif category == 'unsafe_network':
                recommendations.append(
                    f"MEDIUM RISK: Found {count} instances of potentially unsafe network operations. "
                    "Ensure proper input validation, use secure protocols, and implement rate limiting. "
                    "Avoid binding to 0.0.0.0 unless absolutely necessary."
                )
            elif category == 'file_operations':
                recommendations.append(
                    f"LOW RISK: Detected {count} file operations. "
                    "Verify proper file permissions, implement path sanitization, "
                    "and use secure file handling practices."
                )
            elif category == 'crypto_concerns':
                recommendations.append(
                    f"MEDIUM RISK: Found {count} instances of potentially unsafe cryptographic practices. "
                    "Avoid MD5/SHA1, use strong algorithms (SHA256+), and implement proper key management."
                )

        summary = f"Risk Level: {risk_level.upper()}\n\nFindings:\n"
        recommendations = sorted(recommendations, 
                              key=lambda x: "CRITICAL" in x and 3 or "HIGH" in x and 2 or "MEDIUM" in x and 1 or 0,
                              reverse=True)
        return summary + "\n".join(f"- {r}" for r in recommendations)