from datetime import datetime
from pydantic import BaseModel, Field


class RootCauseAnalysis(BaseModel):
    likely_root_cause: str = Field(
        description="The most likely explanation for the incident."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the proposed root cause."
    )

    explanation: str = Field(
        description="Evidence-based explanation of the investigation."
    )

    supporting_evidence: list[str] = Field(
        description="Specific log evidence supporting the conclusion."
    )

    alternative_causes: list[str] = Field(
        description="Other plausible explanations."
    )

    recommended_actions: list[str] = Field(
        description="Suggested steps to investigate or resolve the incident."
    )

    missing_information: list[str] = Field(
        description="Information needed to improve the investigation."
    )


class AIInvestigationHistoryItem(BaseModel):
    investigation_id: str
    status: str
    analysis: RootCauseAnalysis | None = None
    provider: str | None = None
    model: str | None = None
    usage: dict | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class AIInvestigationHistoryResponse(BaseModel):
    incident_id: str
    total: int = Field(ge=0)
    investigations: list[AIInvestigationHistoryItem]


class AIGenerationMetadata(BaseModel):
    provider: str
    model: str
    usage: dict | None = None
    finish_reason: str | None = None

class ModelDiscoveryMetadata(BaseModel):
    total_discovered: int
    provider_discovery_failures: list[str]

class AIInvestigationResponse(BaseModel):
    investigation_id: str
    incident_id: str
    status: str
    analysis: RootCauseAnalysis
    generation: AIGenerationMetadata
    model_discovery: ModelDiscoveryMetadata                