
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.log import (
    LogEntryResponse,
    LogUploadResponse,
    LogSummaryResponse,
    LogAnalysisResponse,
    LogCorrelationResponse
)

from app.services.log_service import (
    process_log_upload,
    get_incident_logs,
    get_log_summary,
    get_log_analysis,
    get_log_correlations
)

router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["Incident Logs"]
)


MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post(
    "/{incident_id}/logs",
    response_model=LogUploadResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_incident_logs(
    incident_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename or ""

    safe_filename = filename.replace("\\", "/").rsplit("/", 1)[-1]

    if not safe_filename or len(safe_filename) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )

    if not safe_filename.lower().endswith((".log", ".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .log and .txt files are supported"
        )

    content_bytes = await file.read(MAX_FILE_SIZE + 1)

    if len(content_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 5 MB limit"
        )

    try:
        content = content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Log file must use UTF-8 encoding"
        )

    return process_log_upload(
        db=db,
        incident_id=incident_id,
        filename=safe_filename,
        content=content
    )


@router.get(
    "/{incident_id}/logs",
    response_model=list[LogEntryResponse]
)
def retrieve_incident_logs(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    return get_incident_logs(
        db,
        incident_id
    )


@router.get("/{incident_id}/logs/summary", response_model=LogSummaryResponse)
def retrieve_log_summary(incident_id: UUID, db: Session = Depends(get_db)):
    return get_log_summary(db, incident_id)



@router.get(
    "/{incident_id}/logs/analysis",
    response_model=LogAnalysisResponse
)
def retrieve_log_analysis(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    return get_log_analysis(db, incident_id)



@router.get(
    "/{incident_id}/logs/correlations",
    response_model=LogCorrelationResponse
)
def retrieve_log_correlations(
    incident_id: UUID,
    db: Session = Depends(get_db)
):
    return get_log_correlations(db, incident_id)