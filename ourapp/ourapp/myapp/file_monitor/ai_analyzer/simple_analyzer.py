from typing import List, Dict
import hashlib
import os
import re
import mimetypes
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    """Advanced security analyzer with detailed threat analysis capabilities"""
    
    def __init__(self):
        # Initialize mime types
        mimetypes.init()
        
        # Define dangerous patterns with more specificity
        self.dangerous_patterns = {
            'command_injection': [
                r'os\.system\(\s*["\'].*(?:rm|del|format|mkfs|dd).*["\']',  # Destructive commands
                r'subprocess\.(call|Popen|getoutput)\(\s*["\'].*(?:rm|del|format|mkfs|dd).*["\']',
                r'exec\(\s*["\'].*(?:rm|del|format|mkfs|dd).*["\']',
                r'eval\(\s*[^)]+\)',  # Dangerous eval usage
                r'shell\s*=\s*True',  # Shell=True is a security risk
            ],
            'hardcoded_credentials': [
                r'password\s*=\s*["\'][^"\']{8,}["\']',  # Looks for longer passwords
                r'secret[\w_]*\s*=\s*["\'][^"\']{8,}["\']',
                r'api[_]?key\s*=\s*["\'][^"\']{8,}["\']',
                r'token\s*=\s*["\'][^"\']{8,}["\']',
                r'credentials\s*=\s*["\'][^"\']{8,}["\']',
                r'auth[\w_]*\s*=\s*["\'][^"\']{8,}["\']'
            ],
            'unsafe_network': [
                r'socket\.socket\(\s*.*,\s*.*SOCK_RAW',  # Raw sockets
                r'bind\(["\']0\.0\.0\.0["\']',  # Binding to all interfaces
                r'requests\.get\(\s*["\']https?://[^"\']+["\'],\s*verify\s*=\s*False',  # Disabled SSL verification
                r'urllib[23]?\.urlopen\(\s*["\']https?://[^"\']+["\'],\s*context=unverified_context', # Unverified context
            ],
            'file_operations': [
                r'open\([^)]+,\s*["\']w["\']',  # Writing to files
                r'\.unlink\(\)',  # File deletion
                r'shutil\.(copy|move|rmtree)',  # File operations
                r'os\.(remove|unlink|rmdir)',  # Deletion operations
            ],
            'crypto_concerns': [
                r'hashlib\.md5\(',  # Weak hashing
                r'hashlib\.sha1\(',  # Weak hashing
                r'random\.random\(',  # Non-cryptographic random
                r'random\.seed\(',  # Predictable seeding
            ],
            'malware_indicators': [
                r'\.encrypt\(',  # Encryption operations (potential ransomware)
                r'\.crypt\(',    # Encryption operations (potential ransomware)
                r'base64\.(?:b64encode|b64decode|encodestring)',  # Obfuscation techniques
                r'exec\(base64\.b64decode',  # Obfuscated code execution
                r'exec\(eval',   # Double execution (very suspicious)
                r'__import__\(["\']subprocess["\']\)',  # Dynamic imports
                r'GetWindowsDirectory|GetSystemDirectory',  # System directory access
                r'CreateProcess|ShellExecute',  # Process creation
                r'WSASocket|socket',  # Network operations
                r'URLDownloadToFile',  # File downloads
                r'AdjustTokenPrivileges',  # Privilege escalation
                r'VirtualAlloc|VirtualProtect',  # Memory manipulation
                r'CreateRemoteThread',  # Process injection
            ]
        }

        # Define more granular dangerous extensions
        self.dangerous_extensions = {
            'executables': [
                '.exe', '.dll', '.sys', '.com', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar', '.bin',
                '.msi', '.scr', '.pif', '.gadget', '.msc', '.cpl'
            ],
            'scripts': [
                '.py', '.rb', '.sh', '.php', '.pl', '.asp', '.aspx', '.jsp', '.cgi', '.htaccess',
                '.psm1', '.psd1', '.ps1xml', '.pssc', '.cdxml'
            ],
            'malware': [
                '.ransomware', '.locked', '.encrypted', '.crypt', '.crypted', '.r5a', '.abc', '.aaa',
                '.ecc', '.ez', '.ezz', '.exx', '.zzz', '.xyz', '.locky', '.cerber', '.zepto',
                '.dharma', '.wallet', '.bip', '.WNCRY', '.osiris', '.kraken'
            ]
        }
        
        # Safe extensions
        self.safe_extensions = [
            '.txt', '.csv', '.md', '.jpg', '.jpeg', '.png', '.gif', '.bmp',
            '.pdf', '.docx', '.xlsx', '.pptx', '.odt', '.rtf', '.ico', '.svg',
            '.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv'
        ]
        
        # Common obfuscation techniques
        self.obfuscation_patterns = [
            r'chr\(\d+\)',  # Character codes
            r'\\x[0-9a-fA-F]{2}',  # Hex encoding
            r'String\.fromCharCode',  # JavaScript obfuscation
            r'eval\(.*\)',  # eval usage
            r'unescape\(',  # URL encoding
            r'document\.write\(.*\)',  # Dynamic content writing
        ]

    def analyze_file(self, file_path: str, file_content: bytes, metadata: dict = None) -> dict:
        """
        Performs a comprehensive security analysis of a file.
        
        Returns a detailed analysis report including:
        - File information
        - Security analysis results
        - Specific threats detected
        - Recommendations based on threats
        """
        if metadata is None:
            metadata = {}

        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Get file extension and type
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Get filename for more specific analysis
        filename = os.path.basename(file_path)
        
        # Get mimetype
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            if self._is_binary_content(file_content[:4096]):
                mime_type = "application/octet-stream"
            else:
                mime_type = "text/plain"
        
        # Initialize threat analysis
        threats = []
        risk_score = 0
        detected_patterns = {}
        detailed_findings = []
        
        # Check for suspicious/dangerous extensions
        extension_risk = self._check_extension_risk(ext)
        if extension_risk['is_risky']:
            threats.append({
                'category': extension_risk['category'],
                'severity': extension_risk['severity'],
                'details': extension_risk['description'],
                'instances': [filename]
            })
            risk_score += extension_risk['severity'] * 10
            detailed_findings.append({
                'type': 'file_extension',
                'severity': self._severity_to_text(extension_risk['severity']),
                'description': extension_risk['description'],
                'recommendation': f"This file has a {extension_risk['category']} extension which may pose security risks. Verify the source before opening."
            })

        # Analyze content if it's a text file
        is_binary = self._is_binary_content(file_content[:4096])
        
        if not is_binary:
            try:
                content_str = file_content.decode('utf-8', errors='replace')
                
                # Check for dangerous patterns
                for category, patterns in self.dangerous_patterns.items():
                    matches = []
                    context_snippets = []
                    
                    for pattern in patterns:
                        found = re.finditer(pattern, content_str, re.IGNORECASE)
                        for match in found:
                            match_text = match.group(0)
                            matches.append(match_text)
                            
                            # Extract context (text around the match)
                            start = max(0, match.start() - 40)
                            end = min(len(content_str), match.end() + 40)
                            context = content_str[start:end].replace('\n', ' ').strip()
                            context_snippets.append(f"...{context}...")
                    
                    if matches:
                        severity = self._get_severity_multiplier(category)
                        
                        # Store detailed info about the matches
                        detected_patterns[category] = {
                            'count': len(matches),
                            'examples': matches[:5],  # Limit to first 5
                            'context': context_snippets[:3]  # Limit to first 3
                        }
                        
                        threats.append({
                            'category': category,
                            'severity': severity,
                            'details': f"Found {len(matches)} instance(s) of {category.replace('_', ' ')}",
                            'instances': matches[:10]  # Limit to first 10
                        })
                        
                        detailed_findings.append({
                            'type': category,
                            'severity': self._severity_to_text(severity),
                            'description': f"Detected {len(matches)} pattern(s) related to {category.replace('_', ' ')}",
                            'examples': context_snippets[:2],
                            'recommendation': self._get_category_recommendation(category)
                        })
                        
                        risk_score += len(matches) * severity * 5
                
                # Check for obfuscation techniques (indicates potential malicious intent)
                obfuscation_matches = []
                for pattern in self.obfuscation_patterns:
                    found = re.finditer(pattern, content_str, re.IGNORECASE)
                    obfuscation_matches.extend([m.group(0) for m in found])
                
                if obfuscation_matches:
                    threats.append({
                        'category': 'code_obfuscation',
                        'severity': 2.5,
                        'details': f"Found {len(obfuscation_matches)} instance(s) of code obfuscation techniques",
                        'instances': obfuscation_matches[:5]
                    })
                    risk_score += len(obfuscation_matches) * 2.5 * 5
                    detailed_findings.append({
                        'type': 'code_obfuscation',
                        'severity': 'HIGH',
                        'description': "Code obfuscation techniques detected",
                        'examples': obfuscation_matches[:2],
                        'recommendation': "Obfuscated code is often used to hide malicious functionality. Review this file carefully."
                    })
            
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
                    'details': 'Binary executable detected',
                    'instances': ['File identified as executable binary']
                })
                risk_score += 25
                detailed_findings.append({
                    'type': 'binary_executable',
                    'severity': 'HIGH',
                    'description': "This file is a binary executable",
                    'recommendation': "Only execute binaries from trusted sources. Scan with antivirus software before running."
                })
            
            # Check executable header (MZ for Windows executables)
            elif file_content.startswith(b'MZ'):
                threats.append({
                    'category': 'windows_executable',
                    'severity': 2.5,
                    'details': 'Windows executable header detected',
                    'instances': ['File contains Windows executable header (MZ)']
                })
                risk_score += 25
                detailed_findings.append({
                    'type': 'windows_executable',
                    'severity': 'HIGH',
                    'description': "This file contains a Windows executable header",
                    'recommendation': "This file appears to be a Windows executable even though it doesn't have a standard executable extension. Treat with caution."
                })
            
            # Check for specific binary signatures
            if len(file_content) > 256:
                # Check for PDF with JavaScript
                if file_content.startswith(b'%PDF') and b'/JavaScript' in file_content[:1024]:
                    threats.append({
                        'category': 'pdf_with_javascript',
                        'severity': 2.0,
                        'details': 'PDF with embedded JavaScript detected',
                        'instances': ['PDF contains JavaScript code which may execute automatically']
                    })
                    risk_score += 20
                    detailed_findings.append({
                        'type': 'pdf_with_javascript',
                        'severity': 'MEDIUM',
                        'description': "PDF contains embedded JavaScript code",
                        'recommendation': "PDFs with JavaScript can execute code when opened. Only open from trusted sources."
                    })
                
                # Check for Office documents with macros
                if b'vbaProject.bin' in file_content or b'word/vbaProject.bin' in file_content:
                    threats.append({
                        'category': 'office_with_macros',
                        'severity': 2.2,
                        'details': 'Office document with macros detected',
                        'instances': ['Document contains VBA macros which may execute automatically']
                    })
                    risk_score += 22
                    detailed_findings.append({
                        'type': 'office_with_macros',
                        'severity': 'HIGH',
                        'description': "Microsoft Office document with embedded macros",
                        'recommendation': "Office macros are a common malware vector. Disable macros and only enable for trusted documents."
                    })

        # Special case for media files - check for unexpectedly small size which might indicate they're not real media files
        if ext in ['.mp4', '.avi', '.mov', '.mkv'] and len(file_content) < 100000:  # Less than 100KB
            threats.append({
                'category': 'suspicious_media_file',
                'severity': 1.5,
                'details': f'Unusually small media file ({len(file_content)} bytes)',
                'instances': ['Media file is suspiciously small']
            })
            risk_score += 15
            detailed_findings.append({
                'type': 'suspicious_media_file',
                'severity': 'MEDIUM',
                'description': f"This media file is unusually small ({len(file_content)} bytes)",
                'recommendation': "This file claims to be a media file but is suspiciously small. It may be masquerading as a media file."
            })

        # Determine overall risk level
        risk_level = self._determine_risk_level(risk_score)

        # Generate detailed recommendation
        recommendation = self._generate_recommendation(detailed_findings, risk_level, filename, ext)

        # Create a complete analysis object
        analysis_result = {
            'file_info': {
                'path': file_path,
                'name': filename,
                'hash': file_hash,
                'extension': ext,
                'size': len(file_content),
                'mime_type': mime_type
            },
            'risk_analysis': {
                'risk_level': risk_level,
                'overall_score': risk_score,
                'threats': threats,
                'detailed_findings': detailed_findings,
                'is_binary': is_binary
            },
            'metadata': metadata,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }

        return analysis_result

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
        """Check if extension is risky with detailed analysis"""
        if ext in self.dangerous_extensions['malware']:
            return {
                'is_risky': True,
                'category': 'malware_extension',
                'severity': 3.0,
                'description': f"File has a known malware extension: {ext}. This extension is commonly associated with ransomware or other malicious software."
            }
        elif ext in self.dangerous_extensions['executables']:
            return {
                'is_risky': True,
                'category': 'executable_extension',
                'severity': 2.0,
                'description': f"File has an executable extension: {ext}. Executable files can run code on your system and may pose security risks if from untrusted sources."
            }
        elif ext in self.dangerous_extensions['scripts']:
            return {
                'is_risky': True,
                'category': 'script_extension',
                'severity': 1.5,
                'description': f"File has a script extension: {ext}. Script files can execute code and may pose security risks if from untrusted sources."
            }
        return {'is_risky': False}

    def _get_severity_multiplier(self, category: str) -> float:
        """Get the severity multiplier for a given threat category"""
        severity_map = {
            'command_injection': 3.0,
            'hardcoded_credentials': 2.0,
            'unsafe_network': 1.5,
            'file_operations': 0.8,
            'crypto_concerns': 1.2,
            'binary_executable': 2.5,
            'windows_executable': 2.5,
            'malware_extension': 3.0,
            'executable_extension': 2.0,
            'script_extension': 1.5,
            'malware_indicators': 3.0,
            'code_obfuscation': 2.5,
            'pdf_with_javascript': 2.0,
            'office_with_macros': 2.2,
            'suspicious_media_file': 1.5
        }
        return severity_map.get(category, 0.5)
    
    def _severity_to_text(self, severity: float) -> str:
        """Convert severity multiplier to text label"""
        if severity >= 2.5:
            return "HIGH"
        elif severity >= 1.5:
            return "MEDIUM"
        else:
            return "LOW"

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine the overall risk level based on risk score"""
        if risk_score >= 50:
            return 'dangerous'
        elif risk_score >= 25:
            return 'suspicious'
        elif risk_score >= 10:
            return 'moderate'
        return 'safe'

    def _get_category_recommendation(self, category: str) -> str:
        """Get a specific recommendation for a threat category"""
        recommendations = {
            'command_injection': "This file contains patterns that could execute commands on your system. Only run code from trusted sources.",
            'hardcoded_credentials': "This file contains what appear to be hardcoded credentials, which is a security risk. Credentials should be stored securely, not in code.",
            'unsafe_network': "This file contains code that makes potentially unsafe network connections. Verify the destinations are trusted.",
            'file_operations': "This file performs operations that could modify other files on your system.",
            'crypto_concerns': "This file uses weak cryptographic methods that may not provide adequate security.",
            'malware_indicators': "This file contains patterns commonly associated with malware. Scan with antivirus immediately.",
            'code_obfuscation': "This file contains obfuscated code which may be hiding malicious functionality."
        }
        return recommendations.get(category, "This pattern may indicate security concerns. Review the code carefully.")

    def _generate_recommendation(self, findings: List[Dict], risk_level: str, filename: str, ext: str) -> str:
        """Generate a detailed recommendation based on all findings"""
        if not findings:
            return "No security concerns detected. The file appears to be safe."

        summary = f"Risk Level: {risk_level.upper()}\n\n"
        
        if risk_level == 'dangerous':
            summary += f"❌ CRITICAL SECURITY ALERT: {filename} has been flagged as DANGEROUS\n\n"
        elif risk_level == 'suspicious':
            summary += f"⚠️ WARNING: {filename} has been flagged as SUSPICIOUS\n\n"
        elif risk_level == 'moderate':
            summary += f"⚠️ CAUTION: {filename} has been flagged with MODERATE risk\n\n"
        
        summary += "Key Findings:\n"
        
        # Sort findings by severity
        sorted_findings = sorted(findings, 
                              key=lambda x: 0 if x['severity'] == 'HIGH' else 1 if x['severity'] == 'MEDIUM' else 2)
        
        for i, finding in enumerate(sorted_findings, 1):
            severity_prefix = {
                'HIGH': '❌ CRITICAL: ',
                'MEDIUM': '⚠️ WARNING: ',
                'LOW': '📝 NOTE: '
            }.get(finding['severity'], '')
            
            summary += f"{i}. {severity_prefix}{finding['description']}\n"
            if 'examples' in finding and finding['examples']:
                summary += f"   Examples: {finding['examples'][0]}\n"
            if 'recommendation' in finding:
                summary += f"   Recommendation: {finding['recommendation']}\n"
            summary += "\n"
        
        # Add general advice based on risk level
        if risk_level == 'dangerous':
            summary += "IMMEDIATE ACTION RECOMMENDED:\n"
            summary += "- Do not open or execute this file\n"
            summary += "- Scan your system with antivirus software\n"
            summary += "- If you've already opened this file, disconnect from networks and seek professional help\n"
        elif risk_level == 'suspicious':
            summary += "CAUTION ADVISED:\n"
            summary += "- Only open this file if you trust the source\n"
            summary += "- Scan with antivirus before proceeding\n"
            summary += "- Monitor your system for unusual behavior\n"
        
        return summary