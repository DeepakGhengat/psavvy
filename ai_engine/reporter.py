"""
AI-Powered Report Generator
Uses ChatGPT for professional report generation
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional
from .providers import AIProviderManager


class ReportGenerator:
    """
    Generates professional penetration testing and security assessment reports
    using AI for comprehensive analysis and clear communication.
    """

    def __init__(self, ai_manager: AIProviderManager):
        self.ai_manager = ai_manager
        self.system_prompt = """You are a professional cybersecurity report writer with expertise in:
- Penetration testing reports
- Vulnerability assessment documentation
- Executive summaries for C-level executives
- Technical details for security teams
- Compliance and regulatory reporting

Write reports that are:
1. Clear and well-structured
2. Appropriate for the target audience
3. Actionable with specific remediation steps
4. Professional in tone
5. Evidence-based with proper documentation

Use standard security report formats and industry best practices."""

    def generate_executive_summary(self, output_dir: str, target: str) -> str:
        """
        Generate executive summary for non-technical stakeholders
        """
        findings = self._collect_findings(output_dir)

        prompt = f"""Generate an executive summary for a security assessment of {target}.

**Scan Results:**
{self._format_findings_brief(findings)}

Create a 1-2 page executive summary including:

## EXECUTIVE SUMMARY

### Assessment Overview
- Target: {target}
- Date: {datetime.now().strftime('%Y-%m-%d')}
- Scope: Automated vulnerability assessment

### Key Findings
- Total vulnerabilities discovered
- Critical/High/Medium/Low breakdown
- Most significant risks

### Risk Rating
Overall security posture: [Critical/High/Medium/Low]
Explanation in business terms

### Immediate Actions Required
Top 3-5 priorities for leadership attention

### Business Impact
- Potential financial impact
- Reputational risks
- Compliance implications

### Recommendations Summary
High-level strategic recommendations

Keep language non-technical and focused on business impact."""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_technical_report(self, output_dir: str, target: str) -> str:
        """
        Generate detailed technical report for security teams
        """
        findings = self._collect_findings(output_dir)

        prompt = f"""Generate a detailed technical security assessment report for {target}.

**Scan Results:**
{self._format_findings(findings)}

Create a comprehensive technical report:

## TECHNICAL SECURITY ASSESSMENT REPORT

### 1. ENGAGEMENT OVERVIEW
- Target: {target}
- Assessment Date: {datetime.now().strftime('%Y-%m-%d')}
- Tools Used: PSAVVY Framework
- Methodology: Automated scanning with AI analysis

### 2. SCOPE & METHODOLOGY
- Testing approach
- Tools and techniques used
- Limitations

### 3. FINDINGS SUMMARY
| Severity | Count | Categories |
|----------|-------|------------|
| Critical |   X   | [types]    |
| High     |   X   | [types]    |
| Medium   |   X   | [types]    |
| Low      |   X   | [types]    |

### 4. DETAILED FINDINGS

For each vulnerability:
#### [FINDING-001] Vulnerability Name
- **Severity:** Critical/High/Medium/Low
- **CVSS Score:** X.X
- **Affected Asset:** URL/Host
- **Description:** Technical details
- **Evidence:** Scanner output
- **Impact:** What an attacker could do
- **Remediation:** Specific fix steps
- **References:** CVE, CWE, OWASP

### 5. REMEDIATION ROADMAP
Prioritized fixes with effort estimates

### 6. APPENDICES
- Raw scan outputs
- Tool configurations
- Testing evidence"""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_finding_detail(self, vuln_type: str, raw_output: str, target: str) -> str:
        """
        Generate detailed finding documentation for a specific vulnerability
        """
        prompt = f"""Generate a detailed finding documentation for:

**Vulnerability Type:** {vuln_type}
**Target:** {target}
**Scanner Output:**
```
{raw_output[:3000]}
```

Create professional finding documentation:

## FINDING: {vuln_type}

### Overview
Brief description of the vulnerability

### Technical Details
- Vulnerability Class: CWE-XXX
- OWASP Category: [relevant category]
- Attack Vector: [how it's exploited]

### Affected Assets
List of affected URLs/endpoints

### Evidence
```
[Relevant scanner output proving the vulnerability]
```

### Proof of Concept
Steps to reproduce:
1. Step 1
2. Step 2
3. ...

### Impact Assessment
- Confidentiality: [None/Low/High]
- Integrity: [None/Low/High]
- Availability: [None/Low/High]
- Potential business impact

### Remediation
#### Immediate Fix
Quick mitigation steps

#### Long-term Solution
Proper remediation approach

#### Code Example
```
[Secure code example if applicable]
```

### References
- CVE links
- Vendor advisories
- OWASP resources"""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_remediation_guide(self, output_dir: str) -> str:
        """
        Generate prioritized remediation guide
        """
        findings = self._collect_findings(output_dir)

        prompt = f"""Generate a remediation guide based on these findings:

{self._format_findings_brief(findings)}

Create a prioritized remediation guide:

## REMEDIATION GUIDE

### Priority Matrix
| Priority | Vulnerability | Effort | Impact | Timeline |
|----------|--------------|--------|--------|----------|
| 1        | [name]       | [H/M/L]| [H/M/L]| [days]   |

### Immediate Actions (0-7 days)
Critical vulnerabilities requiring instant attention:
1. **[Vulnerability]**
   - Why critical: [explanation]
   - Fix: [specific steps]
   - Verification: [how to confirm fixed]

### Short-term Actions (1-4 weeks)
High severity issues:
[Same format]

### Medium-term Actions (1-3 months)
Medium severity issues:
[Same format]

### Long-term Improvements (3-6 months)
Strategic security improvements:
[Same format]

### Resource Requirements
- Personnel needed
- Tools required
- Estimated budget

### Verification Procedures
How to confirm each fix is effective

### Metrics & KPIs
How to measure remediation progress"""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_compliance_report(self, output_dir: str, framework: str) -> str:
        """
        Map findings to compliance framework requirements
        """
        findings = self._collect_findings(output_dir)

        prompt = f"""Map security findings to {framework} compliance requirements:

**Findings:**
{self._format_findings_brief(findings)}

Generate a compliance-focused report:

## {framework} COMPLIANCE ASSESSMENT

### Compliance Summary
Overall compliance status: [Compliant/Partially Compliant/Non-Compliant]

### Findings Mapped to Requirements

| {framework} Requirement | Status | Findings | Gap Description |
|------------------------|--------|----------|-----------------|
| [Req ID] [Description] | [Pass/Fail] | [Related findings] | [Gap details] |

### Detailed Gap Analysis

#### [Requirement ID] - Requirement Name
- **Status:** Pass/Fail
- **Related Findings:** [list]
- **Gap Description:** [what's missing]
- **Remediation for Compliance:** [specific steps]
- **Evidence Needed:** [documentation required]

### Remediation Priorities for Compliance
Order fixes to achieve compliance fastest

### Compliance Roadmap
Timeline to achieve full compliance

### Documentation Recommendations
What documentation to create/update"""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_full_report(self, output_dir: str, target: str, report_type: str = "standard") -> Dict[str, str]:
        """
        Generate complete report package
        """
        reports = {}

        # Generate all report sections
        reports["executive_summary"] = self.generate_executive_summary(output_dir, target)
        reports["technical_report"] = self.generate_technical_report(output_dir, target)
        reports["remediation_guide"] = self.generate_remediation_guide(output_dir)

        # Combine into final report
        final_report = f"""# SECURITY ASSESSMENT REPORT
## Target: {target}
## Date: {datetime.now().strftime('%Y-%m-%d')}
## Generated by: PSAVVY AI Security Framework

---

{reports['executive_summary']}

---

{reports['technical_report']}

---

{reports['remediation_guide']}

---

## APPENDIX A: Raw Scan Data

See output directory for complete scanner outputs.

---

*This report was generated using AI-assisted analysis.
All findings should be manually verified before remediation.*
"""
        reports["full_report"] = final_report

        return reports

    def save_report(self, report: str, output_path: str):
        """
        Save report to file
        """
        with open(output_path, 'w') as f:
            f.write(report)
        return output_path

    def _collect_findings(self, output_dir: str) -> Dict[str, str]:
        """Collect all findings from output directory"""
        findings = {}

        if not os.path.exists(output_dir):
            return findings

        for filepath in glob.glob(os.path.join(output_dir, "*.txt")):
            try:
                with open(filepath, 'r', errors='ignore') as f:
                    content = f.read()
                    if content.strip():
                        findings[os.path.basename(filepath)] = content
            except Exception as e:
                findings[os.path.basename(filepath)] = f"Error reading: {str(e)}"

        return findings

    def _format_findings(self, findings: Dict[str, str]) -> str:
        """Format findings for AI prompt - detailed"""
        formatted = []
        for filename, content in findings.items():
            truncated = content[:4000] if len(content) > 4000 else content
            formatted.append(f"=== {filename} ===\n{truncated}\n")
        return "\n".join(formatted)

    def _format_findings_brief(self, findings: Dict[str, str]) -> str:
        """Format findings for AI prompt - brief summary"""
        formatted = []
        for filename, content in findings.items():
            # Take first 1000 chars for brief summary
            truncated = content[:1000] if len(content) > 1000 else content
            formatted.append(f"[{filename}]: {truncated[:500]}...")
        return "\n".join(formatted)
