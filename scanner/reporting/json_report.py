"""JSON report generator."""

import json
from typing import Dict, Any


def generate_json_report(scan_data: Dict[str, Any]) -> str:
    """Generate pretty-printed JSON report."""
    return json.dumps(scan_data, indent=2)
