"""HTML report generator."""

from typing import Dict, Any
from html import escape


def generate_html_report(scan_data: Dict[str, Any]) -> str:
    """Generate standalone HTML report."""
    summary = scan_data.get("summary", {})
    domains = scan_data.get("domains", [])
    findings = scan_data.get("findings", [])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSDLC Security Assessment Report - {escape(scan_data.get('project', 'Unknown'))}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; line-height: 1.6; color: #1a1a1a; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        .header {{ background: #fff; padding: 40px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 32px; margin-bottom: 10px; color: #0a0a0a; }}
        .meta {{ color: #666; font-size: 14px; }}
        .score-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 8px; margin-bottom: 30px; text-align: center; }}
        .score-card h2 {{ font-size: 64px; margin-bottom: 10px; }}
        .score-card p {{ font-size: 18px; opacity: 0.9; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .card h3 {{ font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }}
        .card .value {{ font-size: 36px; font-weight: 700; color: #0a0a0a; }}
        .section {{ background: white; padding: 40px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h2 {{ font-size: 24px; margin-bottom: 20px; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #f0f0f0; }}
        th {{ background: #f8f8f8; font-weight: 600; }}
        .finding {{ padding: 20px; border-left: 4px solid #ddd; margin-bottom: 20px; background: #fafafa; border-radius: 4px; }}
        .finding.fail {{ border-left-color: #dc3545; }}
        .finding.pass {{ border-left-color: #28a745; }}
        .finding.warn {{ border-left-color: #ffc107; }}
        .finding.skip {{ border-left-color: #6c757d; }}
        .finding h4 {{ font-size: 18px; margin-bottom: 10px; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
        .badge.critical {{ background: #dc3545; color: white; }}
        .badge.high {{ background: #fd7e14; color: white; }}
        .badge.medium {{ background: #ffc107; color: #000; }}
        .badge.low {{ background: #17a2b8; color: white; }}
        .badge.pass {{ background: #28a745; color: white; }}
        .badge.fail {{ background: #dc3545; color: white; }}
        .badge.skip {{ background: #6c757d; color: white; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 13px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 4px; overflow-x: auto; }}
        .footer {{ text-align: center; color: #999; font-size: 14px; margin-top: 40px; padding: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ SSDLC Security Assessment Report</h1>
            <div class="meta">
                <strong>Project:</strong> {escape(scan_data.get('project', 'Unknown'))} |
                <strong>Scan ID:</strong> {escape(scan_data.get('scan_id', 'N/A'))} |
                <strong>Date:</strong> {escape(scan_data.get('started_at', 'N/A'))}
            </div>
        </div>

        <div class="score-card">
            <h2>{summary.get('score', 0)}/100</h2>
            <p>Security Maturity Score | Risk Level: <strong>{escape(summary.get('risk_level', 'UNKNOWN'))}</strong></p>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Total Checks</h3>
                <div class="value">{summary.get('total_checks', 0)}</div>
            </div>
            <div class="card">
                <h3>Passed</h3>
                <div class="value" style="color: #28a745;">{summary.get('passed', 0)}</div>
            </div>
            <div class="card">
                <h3>Failed</h3>
                <div class="value" style="color: #dc3545;">{summary.get('failed', 0)}</div>
            </div>
            <div class="card">
                <h3>Critical Findings</h3>
                <div class="value" style="color: #dc3545;">{summary.get('critical', 0)}</div>
            </div>
        </div>

        <div class="section">
            <h2>Domain Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Domain</th>
                        <th>Score</th>
                        <th>Passed / Total</th>
                        <th>Failed</th>
                    </tr>
                </thead>
                <tbody>"""

    for domain in domains:
        score = domain.get("score", 0)
        html += f"""
                    <tr>
                        <td><strong>{escape(domain.get('domain', ''))}</strong></td>
                        <td>{score}%</td>
                        <td>{domain.get('passed', 0)} / {domain.get('total', 0)}</td>
                        <td>{domain.get('failed', 0)}</td>
                    </tr>"""

    html += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Detailed Findings</h2>"""

    for finding in findings:
        status = finding.get("status", "").lower()
        severity = finding.get("severity", "").lower()
        name = escape(finding.get("name", ""))
        detail = escape(finding.get("detail", ""))
        evidence = escape(finding.get("evidence", ""))
        remediation = escape(finding.get("remediation", ""))

        severity_badge = f'<span class="badge {severity}">{severity.upper()}</span>' if severity else ''
        status_badge = f'<span class="badge {status}">{status.upper()}</span>'

        html += f"""
            <div class="finding {status}">
                <h4>{name} {severity_badge} {status_badge}</h4>
                <p><strong>{escape(finding.get('domain', ''))} / {escape(finding.get('category', ''))}</strong></p>
                <p>{detail}</p>"""

        if evidence:
            html += f"""
                <p><strong>Evidence:</strong></p>
                <pre><code>{evidence}</code></pre>"""

        if remediation:
            html += f"""
                <p><strong>Remediation:</strong></p>
                <p>{remediation}</p>"""

        html += """
            </div>"""

    html += """
        </div>

        <div class="footer">
            <p><strong>Assessment Limitations:</strong> Static analysis provides a snapshot of detectable security patterns. A clean scan does not guarantee absence of vulnerabilities.</p>
            <p>Generated by SSDLC Analyzer v2.0.0</p>
        </div>
    </div>
</body>
</html>"""

    return html
