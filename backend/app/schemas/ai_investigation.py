from pydantic import BaseModel, Field

class RootCauseAnalysis(BaseModel):
    likely_root_cause: str = Field(
        description= "The most likely explanation for the incident."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description= "Confidence in the proposed root cause."
    )

    explanation: str = Field(
        description= "Evidence-based explanation of the investigation."
    )

    supporting_evidence: list[str] = Field(
        description= "Specific log evidence supporting the conclusion."
    )

    alternative_causes: list[str] = Field(
        description= "Other plausible explanations."
    )

    recommended_actions: list[str] = Field(
        description= "Suggested steps to investigate or resolve the incident."
    )

    missing_information: list[str] = Field(
        description= "Information needed to improve the investigation."
    )