from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import tempfile
import zipfile
import shutil
import os

from scanner.checks import requirements
from scanner.checks import architecture
from scanner.checks import implementation
from scanner.checks import testing
from scanner.score import calculate_score


app = FastAPI(
    title="SSDLC Analyzer API",
    description="API for analyzing Secure Software Development Lifecycle maturity",
    version="1.0.0",
)


# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "SSDLC Analyzer API is running",
        "status": "online",
    }


@app.post("/scan")
async def scan_project(file: UploadFile = File(...)):

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

        zip_path = os.path.join(
            temp_dir,
            safe_filename,
        )

        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extract_dir = os.path.join(
            temp_dir,
            "project",
        )

        os.makedirs(extract_dir)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:

            # Basic ZIP validation
            for member in zip_ref.infolist():

                member_path = os.path.abspath(
                    os.path.join(
                        extract_dir,
                        member.filename,
                    )
                )

                if not member_path.startswith(
                    os.path.abspath(extract_dir)
                    + os.sep
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="Unsafe ZIP file detected.",
                    )

            zip_ref.extractall(extract_dir)

        results = []

        results.extend(
            requirements.run_all(extract_dir)
        )

        results.extend(
            architecture.run_all(extract_dir)
        )

        results.extend(
            implementation.run_all(extract_dir)
        )

        results.extend(
            testing.run_all(extract_dir)
        )

        score = calculate_score(results)

        passed_checks = sum(
            1
            for result in results
            if result["passed"]
        )

        failed_checks = sum(
            1
            for result in results
            if not result["passed"]
        )

        return {
            "project": safe_filename,
            "score": score,
            "total_checks": len(results),
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "results": results,
        }

    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid ZIP archive.",
        )

    except HTTPException:
        raise

    except Exception as error:
        return {
            "error": f"Scan failed: {str(error)}"
        }

    finally:
        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )