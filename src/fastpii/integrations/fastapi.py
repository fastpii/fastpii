from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from fastpii import FastPII, DEFAULT_PRIORITY, DEFAULT_CONFIDENCE_SCORES, DEFAULT_CONTEXT_BOOST
from fastpii.core.confidence import ConfidenceScorer
from fastpii.countries import get_country_pack


__all__ = [
    "DetectRequest",
    "ValidateRequest",
    "FindingResponse",
    "DetectionResponse",
    "ValidationResponse",
    "DetectorInfo",
    "create_app",
    "app",
]


class DetectRequest(BaseModel):
    text: str
    regions: list[str]
    detector_names: list[str] | None = None


class ValidateRequest(BaseModel):
    value: str
    detector_name: str
    regions: list[str]


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


def _build_engine(regions: list[str]) -> FastPII:
    scorer = ConfidenceScorer(
        base_scores=DEFAULT_CONFIDENCE_SCORES,
        context_boost=DEFAULT_CONTEXT_BOOST,
    )
    engine = FastPII(priority=DEFAULT_PRIORITY, confidence_scorer=scorer)
    for region_code in regions:
        pack_cls = get_country_pack(region_code)
        if pack_cls is not None:
            engine.register(pack_cls())
    return engine


def create_app(engine: FastPII | None = None) -> FastAPI:
    app = FastAPI(
        title="FastPII API",
        description="Czech and Central European PII Detection API",
        version="0.2.0"
    )

    @app.post("/detect", response_model=DetectionResponse)
    async def detect_pii(request: DetectRequest):
        app_engine = engine or _build_engine(request.regions)
        result = app_engine.detect(request.text, detector_names=request.detector_names)

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
        app_engine = engine or _build_engine(request.regions)
        try:
            result = app_engine.validate(request.value, detector_name=request.detector_name)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Detector '{request.detector_name}' not found")

        return ValidationResponse(
            detector=result.detector,
            value=result.value,
            is_valid=result.is_valid,
            metadata=result.metadata
        )

    @app.get("/detectors", response_model=list[DetectorInfo])
    async def list_detectors(regions: list[str] | None = Query(None)):
        if engine is not None:
            detectors = engine.list_detectors()
        else:
            if regions is None:
                raise HTTPException(status_code=400, detail="regions parameter is required when no engine is pre-configured")
            app_engine = _build_engine(regions)
            detectors = app_engine.list_detectors()

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
