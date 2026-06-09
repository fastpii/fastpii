from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastpii import PrivacyGuard


class DetectRequest(BaseModel):
    text: str
    regions: list[str] = ["cz"]
    detector_names: list[str] | None = None


class ValidateRequest(BaseModel):
    value: str
    detector_name: str
    regions: list[str] = ["cz"]


class FindingResponse(BaseModel):
    type: str
    value: str
    start: int
    end: int
    confidence: float
    region: str
    metadata: dict[str, object]


class DetectionResponse(BaseModel):
    text: str
    findings: list[FindingResponse]
    detector_names: list[str]
    processing_time_ms: int


class ValidationResponse(BaseModel):
    detector: str
    value: str
    is_valid: bool
    metadata: dict[str, object]


class DetectorInfo(BaseModel):
    name: str
    region: str
    description: str


def create_app() -> FastAPI:
    app = FastAPI(
        title="FastPII API",
        description="Czech and Central European PII Detection API",
        version="0.1.0"
    )

    @app.post("/detect", response_model=DetectionResponse)
    async def detect_pii(request: DetectRequest):
        guard = PrivacyGuard(regions=request.regions)
        result = guard.detect(request.text, detector_names=request.detector_names)
        
        return DetectionResponse(
            text=result.text,
            findings=[
                FindingResponse(
                    type=f.type,
                    value=f.value,
                    start=f.start,
                    end=f.end,
                    confidence=f.confidence,
                    region=f.region,
                    metadata=f.metadata
                )
                for f in result.findings
            ],
            detector_names=result.detector_names,
            processing_time_ms=result.processing_time_ms
        )

    @app.post("/validate", response_model=ValidationResponse)
    async def validate_identifier(request: ValidateRequest):
        guard = PrivacyGuard(regions=request.regions)
        
        try:
            result = guard.validate(request.value, detector_name=request.detector_name)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Detector '{request.detector_name}' not found")
        
        return ValidationResponse(
            detector=result.detector,
            value=result.value,
            is_valid=result.is_valid,
            metadata=result.metadata
        )

    @app.get("/detectors", response_model=list[DetectorInfo])
    async def list_detectors(regions: list[str] | None = None):
        guard = PrivacyGuard(regions=regions or ["cz"])
        detectors = guard.list_detectors()
        
        return [
            DetectorInfo(
                name=d.name,
                region=d.region,
                description=d.description
            )
            for d in detectors
        ]

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


app = create_app()
