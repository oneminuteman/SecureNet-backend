from typing import List, Dict
import hashlib
import os
import re
import mimetypes
import logging

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    def __init__(self):
        # Initialize mime types
        mimetypes.init()
        
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

        # Known dangerous extensions
        self.dangerous_extensions = {
            'executables': ['.exe', '.dll', '.sys', '.com', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar', '.bin'],
            'scripts': ['.py', '.rb', '.sh', '.php', '.pl', '.asp', '.aspx', '.jsp', '.cgi'],
            'malware': ['.ransomware', '.locked', '.encrypted', '.crypt', '.crypted', '.r5a', '.abc', '.aaa']
        }
        
        # Safe extensions
        self.safe_extensions = [
            '.txt', '.csv', '.md', '.jpg', '.jpeg', '.png', '.gif', '.bmp',
            '.pdf', '.docx', '.xlsx', '.pptx', '.odt', '.rtf', '.ico'
        ]

    def analyze_file(self, file_path: str, file_content: bytes, metadata: dict = None) -> dict:
        """
        Analyzes a file for security concerns and returns a detailed analysis report.
        """
        if metadata is None:
            metadata = {}

        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Get file extension and type
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Get mimetype using standard library
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            if self._is_binary_content(file_content[:1024]):
                mime_type = "application/octet-stream"
            else:
                mime_type = "text/plain"
        
        # Initialize threat analysis
        threats = []
        risk_score = 0
        
        # Check for suspicious/dangerous extensions
        extension_risk = self._check_extension_risk(ext)
        if extension_risk['is_risky']:
            threats.append({
                'category': extension_risk['category'],
                'severity': extension_risk['severity'],
                'instances': [f"{extension_risk['description']}"]
            })
            risk_score += extension_risk['severity'] * 10

        # Analyze content if it's a text file
        is_binary = self._is_binary_content(file_content[:1024])
        
        if not is_binary:
            try:
                content_str = file_content.decode('utf-8', errors='replace')
                
                # Check for general dangerous patterns
                for category, patterns in self.dangerous_patterns.items():
                    matches = []
                    for pattern in patterns:
                        found = re.finditer(pattern, content_str, re.IGNORECASE)
                        matches.extend([m.group(0) for m in found])
                    
                    if matches:
                        severity = self._get_severity_multiplier(category)
                        threats.append({
                            'category': category,
                            'severity': severity,
                            'instances': matches[:10]  # Limit to first 10 matches
                        })
                        risk_score += len(matches) * severity * 5
            
            except UnicodeDecodeError:
                is_binary = True  # Failed to decode as text
        
        # Binary file analysis
        if is_binary:
            # Check for executable files
            if mime_type and (mime_type.startswith('application/x-executable') or 
                             mime_type.startswith('application/x-msdownload')):
                threats.append({
                    'category': 'binary_executable',
                    'severity': 2.5,
                    'instances': ['Binary executable detected']
                })
                risk_score += 25
            
            # Check executable header (MZ for Windows executables)
            elif file_content.startswith(b'MZ'):
                threats.append({
                    'category': 'windows_executable',
                    'severity': 2.5,
                    'instances': ['Windows executable header detected']
                })
                risk_score += 25

        # Determine overall risk level
        risk_level = self._determine_risk_level(risk_score)

        # Generate recommendation
        recommendation = self._generate_recommendation(threats, risk_level, ext)

        return {
            'file_info': {
                'path': file_path,
                'hash': file_hash,
                'extension': ext,
                'size': len(file_content),
                'mime_type': mime_type
            },
            'risk_analysis': {
                'risk_level': risk_level,
                'overall_score': risk_score,
                'threats': threats,
                'is_binary': is_binary
            },
            'metadata': metadata,
            'recommendation': recommendation
        }

    def _is_binary_content(self, sample: bytes) -> bool:
        """Determine if content is binary by checking for null bytes and control characters"""
        # Quick check for null bytes
        if b'\x00' in sample:
            return True
            
        # Check for high concentration of control characters
        control_chars = 0
        for byte in sample:
            if byte < 32 and byte not in (9, 10, 13):  # Tab, LF, CR are acceptable
                control_chars += 1
                
        # If more than 30% are control chars, likely binary
        return (control_chars / len(sample)) > 0.3 if sample else False

    def _check_extension_risk(self, ext: str) -> dict:
        """Check if extension is risky"""
        if ext in self.dangerous_extensions['malware']:
            return {
                'is_risky': True,
                'category': 'malware_extension',
                'severity': 3.0,
                'description': f"File has a known malware extension: {ext}"
            }
        elif ext in self.dangerous_extensions['executables']:
            return {
                'is_risky': True,
                'category': 'executable_extension',
                'severity': 2.0,
                'description': f"File has an executable extension: {ext}"
            }
        elif ext in self.dangerous_extensions['scripts']:
            return {
                'is_risky': True,
                'category': 'script_extension',
                'severity': 1.5,
                'description': f"File has a script extension: {ext}"
            }
        return {'is_risky': False}

    def _get_severity_multiplier(self, category: str) -> float:
        multiplier_map = {
            'command_injection': 3.0,
            'hardcoded_credentials': 2.0,
            'unsafe_network': 1.5,
            'file_operations': 0.8,
            'crypto_concerns': 1.2,
            'binary_executable': 2.5,
            'windows_executable': 2.5,
            'malware_extension': 3.0,
            'executable_extension': 2.0,
            'script_extension': 1.5
        }
        return multiplier_map.get(category, 0.5)

    def _determine_risk_level(self, risk_score: float) -> str:
        if risk_score >= 70:
            return 'dangerous'
        elif risk_score >= 30:
            return 'suspicious'
        return 'safe'

    def _generate_recommendation(self, threats: List[Dict], risk_level: str, ext: str) -> str:
        if not threats:
            return "No security concerns detected. The file appears to be safe."

        recommendations = []
        for threat in threats:
            category = threat['category']
            count = len(threat['instances'])
            
            if category == 'command_injection':
                recommendations.append(
                    f"CRITICAL: Found {count} instances of potential command injection. "
                    "Replace os.system/exec calls with subprocess.run with proper argument escaping. "
                    "Always validate and sanitize input before execution."
                )
            elif category == 'hardcoded_credentials':
                recommendations.append(
                    f"HIGH RISK: Detected {count} potential hardcoded credentials. "
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
            elif category == 'binary_executable' or category == 'windows_executable':
                recommendations.append(
                    f"HIGH RISK: Binary executable file detected. "
                    "Verify the source and authenticity of the executable. "
                    "Consider running through antivirus scanning before execution."
                )
            elif category == 'malware_extension':
                recommendations.append(
                    f"CRITICAL: File has an extension commonly associated with malware or ransomware. "
                    "Quarantine the file immediately and scan with antivirus software. "
                    "If this is a ransomware attack, disconnect from network and notify security team."
                )
            elif category == 'executable_extension':
                recommendations.append(
                    f"HIGH RISK: File has an executable extension. "
                    "Only run executables from trusted sources after verification. "
                    "Use antivirus scanning before execution."
                )
            elif category == 'script_extension':
                recommendations.append(
                    f"MEDIUM RISK: File has a script extension that can execute code. "
                    "Review the script contents before execution. "
                    "Consider running in a restricted environment."
                )

        summary = f"Risk Level: {risk_level.upper()}\n\nFindings:\n"
        recommendations = sorted(recommendations, 
                              key=lambda x: "CRITICAL" in x and 3 or "HIGH" in x and 2 or "MEDIUM" in x and 1 or 0,
                              reverse=True)
        return summary + "\n".join(f"- {r}" for r in recommendations)