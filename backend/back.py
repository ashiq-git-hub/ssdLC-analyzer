from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import tempfile
import zipfile
import shutil
import os

from scanner.engine import scan_repository
from scanner.utils.archive import safe_extract_zip, ArchiveSecurityError
from scanner import db


app = FastAPI(
    title="SSDLC Analyzer API",
    description="API for analyzing Secure Software Development Lifecycle maturity",
    version="2.0.0",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response models
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


class ScanSummaryResponse(BaseModel):
    score: float
    risk_level: str
    total_checks: int
    passed: int
    failed: int
    warnings: int
    errors: int
    skipped: int
    critical: int
    high: int
    medium: int
    low: int
    info: int


class DomainScoreResponse(BaseModel):
    domain: str
    score: float
    weight: float
    total: int
    passed: int
    failed: int
    warnings: int
    errors: int
    skipped: int


class FindingResponse(BaseModel):
    id: str
    domain: str
    category: str
    name: str
    status: str
    severity: Optional[str] = None
    confidence: Optional[str] = None
    description: str
    detail: str
    remediation: str
    evidence: str
    files: List[str]
    line: Optional[int] = None
    tool: str
    rule_id: Optional[str] = None
    references: List[str]
    metadata: Dict[str, Any]
    passed: bool


class ScanResultResponse(BaseModel):
    scan_id: str
    project: str
    started_at: str
    completed_at: Optional[str]
    status: str
    summary: Optional[ScanSummaryResponse]
    domains: List[DomainScoreResponse]
    findings: List[FindingResponse]
    metadata: Dict[str, Any]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# Initialize database on startup
db.init_db()


@app.get("/", response_model=HealthResponse)
def home():
    """API health check endpoint."""
    return {
        "status": "online",
        "message": "SSDLC Analyzer API is running",
        "version": "2.0.0",
    }


@app.get("/health", response_model=HealthResponse)
def health():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "message": "All systems operational",
        "version": "2.0.0",
    }


@app.post("/scan", response_model=ScanResultResponse)
async def scan_project(file: UploadFile = File(...)):
    """
    Scan a repository ZIP file for SSDLC security maturity.

    Args:
        file: ZIP archive containing the project repository

    Returns:
        Complete scan results with findings and scores
    """
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a ZIP file containing the project.",
        )

    temp_dir = tempfile.mkdtemp()

    try:
        safe_filename = os.path.basename(file.filename)
        zip_path = os.path.join(temp_dir, safe_filename)

        # Save uploaded file
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extract_dir = os.path.join(temp_dir, "project")

        # Secure extraction with validation
        try:
            project_root = safe_extract_zip(zip_path, extract_dir)
        except ArchiveSecurityError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )

        # Run scan
        result = scan_repository(project_root)

        # Store in database
        result_dict = result.to_dict()
        db.save_scan(result_dict)

        # Return response
        return result_dict

    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid ZIP archive.",
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {str(error)}",
        )

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/scans")
def list_scans(limit: int = 50):
    """
    List all scan history summaries.

    Args:
        limit: Maximum number of scans to return

    Returns:
        List of scan summaries
    """
    scans = db.list_scans(limit=limit)
    return {"scans": scans, "total": len(scans)}


@app.get("/scans/{scan_id}", response_model=ScanResultResponse)
def get_scan(scan_id: str):
    """
    Retrieve a specific scan result by ID.

    Args:
        scan_id: Scan identifier

    Returns:
        Complete scan result
    """
    scan_data = db.get_scan(scan_id)

    if not scan_data:
        raise HTTPException(
            status_code=404,
            detail=f"Scan {scan_id} not found",
        )

    return scan_data


@app.delete("/scans/{scan_id}")
def delete_scan_endpoint(scan_id: str):
    """
    Delete a scan from history.

    Args:
        scan_id: Scan identifier

    Returns:
        Deletion confirmation
    """
    deleted = db.delete_scan(scan_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Scan {scan_id} not found",
        )

    return {
        "message": f"Scan {scan_id} deleted successfully",
        "scan_id": scan_id,
    }


@app.get("/scans/{scan_id}/report")
def get_scan_report(scan_id: str, format: str = "json"):
    """
    Generate a report for a specific scan.

    Args:
        scan_id: Scan identifier
        format: Report format (json, markdown, html)

    Returns:
        Formatted report
    """
    scan_data = db.get_scan(scan_id)

    if not scan_data:
        raise HTTPException(
            status_code=404,
            detail=f"Scan {scan_id} not found",
        )

    if format == "json":
        return scan_data

    # TODO: Implement markdown and html report generation
    return {"message": f"Report format '{format}' not yet implemented"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
