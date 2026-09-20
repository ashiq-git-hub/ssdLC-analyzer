"""
SQLite database storage for scan history.

Provides persistent storage for SSDLC security assessment results.
"""

import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime


DB_FILE = os.path.join(os.path.dirname(__file__), "..", "ssdlc_scans.db")


def init_db(db_path: Optional[str] = None):
    """Initialize SQLite database with required tables."""
    path = db_path or DB_FILE
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            status TEXT NOT NULL,
            score REAL,
            risk_level TEXT,
            total_checks INTEGER,
            passed INTEGER,
            failed INTEGER,
            warnings INTEGER,
            errors INTEGER,
            skipped INTEGER,
            critical INTEGER,
            high INTEGER,
            medium INTEGER,
            low INTEGER,
            info INTEGER,
            data_json TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_scan(scan_data: Dict[str, Any], db_path: Optional[str] = None) -> None:
    """Save complete scan result to SQLite."""
    path = db_path or DB_FILE
    init_db(path)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    summary = scan_data.get("summary", {})

    cursor.execute("""
        INSERT OR REPLACE INTO scans (
            scan_id, project, started_at, completed_at, status,
            score, risk_level, total_checks, passed, failed,
            warnings, errors, skipped, critical, high, medium, low, info,
            data_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_data.get("scan_id"),
        scan_data.get("project"),
        scan_data.get("started_at"),
        scan_data.get("completed_at"),
        scan_data.get("status"),
        summary.get("score"),
        summary.get("risk_level"),
        summary.get("total_checks"),
        summary.get("passed"),
        summary.get("failed"),
        summary.get("warnings"),
        summary.get("errors"),
        summary.get("skipped"),
        summary.get("critical"),
        summary.get("high"),
        summary.get("medium"),
        summary.get("low"),
        summary.get("info"),
        json.dumps(scan_data)
    ))

    conn.commit()
    conn.close()


def get_scan(scan_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve full scan result by ID."""
    path = db_path or DB_FILE
    init_db(path)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("SELECT data_json FROM scans WHERE scan_id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return None


def list_scans(limit: int = 50, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """List recent scan summaries."""
    path = db_path or DB_FILE
    init_db(path)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT scan_id, project, started_at, completed_at, status,
               score, risk_level, total_checks, passed, failed, critical, high
        FROM scans
        ORDER BY started_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    scans = []
    for row in rows:
        scans.append({
            "scan_id": row[0],
            "project": row[1],
            "started_at": row[2],
            "completed_at": row[3],
            "status": row[4],
            "score": row[5],
            "risk_level": row[6],
            "total_checks": row[7],
            "passed": row[8],
            "failed": row[9],
            "critical": row[10],
            "high": row[11],
        })

    return scans


def delete_scan(scan_id: str, db_path: Optional[str] = None) -> bool:
    """Delete a scan from SQLite."""
    path = db_path or DB_FILE
    init_db(path)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM scans WHERE scan_id = ?", (scan_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted
