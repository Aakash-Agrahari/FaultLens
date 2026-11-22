import re
import json
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.schemas.ai_investigation import RootCauseAnalysis

from app.services.investigation_service import investigate_incident
from app.services.ai_prompt_builder import build_investigation_prompt

from app.ai.providers.base import GenerationRequest
from app.ai.router.provider_registry import provider_registry
from app.ai.router.provider_setup import initialize_providers
from app.ai.router.model_catalog import ModelCatalog
from app.ai.router.model_selector import ModelSelector
from app.ai.router.model_eligibility import ModelRequirements
from app.ai.router.fallback_executor import (
    FallbackExecutor,
    FallbackExecutionError,
)


def serialize_log_entry(entry):
    """Convert a database log entry into plain Python data."""

    return {
        "id": str(entry.id),
        "source_file": entry.source_file,
        "line_number": entry.line_number,
        "timestamp": (
            entry.timestamp.isoformat()
            if entry.timestamp else None
        ),
        "level": entry.level,
        "message": entry.message[:2000]
    }


def prepare_ai_investigation(db: Session, incident_id: UUID):
    """Prepare incident evidence and provider-independent prompts."""

    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    report = investigate_incident(db, incident_id)

    incident_context = {
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "created_at": incident.created_at.isoformat()
    }

    summary = report["summary"]
    pattern_analysis = report["pattern_analysis"]
    correlations = report["correlations"]
    anomalies = report["anomalies"]

    summary_context = {
        "total_entries": summary["total_entries"],
        "level_counts": summary["level_counts"],
        "first_timestamp": (
            summary["first_timestamp"].isoformat()
            if summary["first_timestamp"] else None
        ),
        "last_timestamp": (
            summary["last_timestamp"].isoformat()
            if summary["last_timestamp"] else None
        ),
        "recent_errors": [
            serialize_log_entry(entry)
            for entry in summary["recent_errors"]
        ]
    }

    pattern_context = [
        {
            "rule_id": finding["rule_id"],
            "title": finding["title"],
            "severity": finding["severity"],
            "description": finding["description"],
            "occurrences": finding["occurrences"],
            "evidence": [
                serialize_log_entry(entry)
                for entry in finding["evidence"][:5]
            ]
        }
        for finding in pattern_analysis["findings"]
    ]

    correlation_context = [
        {
            "event_count": group["event_count"],
            "start_timestamp": group["start_timestamp"].isoformat(),
            "end_timestamp": group["end_timestamp"].isoformat(),
            "events": [
                serialize_log_entry(entry)
                for entry in group["events"][:5]
            ]
        }
        for group in correlations["groups"][:10]
    ]

    anomaly_context = [
        {
            "bucket_start": anomaly["bucket_start"].isoformat(),
            "bucket_end": anomaly["bucket_end"].isoformat(),
            "event_count": anomaly["event_count"],
            "baseline_count": anomaly["baseline_count"],
            "threshold": anomaly["threshold"],
            "evidence": [
                serialize_log_entry(entry)
                for entry in anomaly["evidence"][:5]
            ]
        }
        for anomaly in anomalies["anomalies"][:5]
    ]

    evidence_context = {
        "summary": summary_context,
        "pattern_findings": pattern_context,
        "correlation_groups": correlation_context,
        "anomalies": anomaly_context
    }

    system_prompt, user_prompt = build_investigation_prompt(
        incident_context=incident_context,
        evidence_context=evidence_context
    )

    # Include the exact response schema in the prompt.
    response_schema = RootCauseAnalysis.model_json_schema()

    system_prompt += (
        "\n\nREQUIRED JSON SCHEMA:\n"
        + json.dumps(response_schema, indent=2)
        + "\nReturn only valid JSON matching this schema. "
        "Do not wrap the JSON in Markdown."
    )

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt
    }


def parse_root_cause_result(content: str) -> RootCauseAnalysis:
    """Parse and validate the model response."""

    content = content.strip()

    # Remove Markdown JSON fences if a model adds them.
    if content.startswith("```"):
        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE
        )
        content = re.sub(r"\s*```$", "", content)

    return RootCauseAnalysis.model_validate_json(content)


def validate_generation_result(result):
    """Reject invalid model responses so fallback can continue."""

    parse_root_cause_result(result.content)


async def run_ai_investigation(db: Session, incident_id: UUID):
    """Run a complete AI-powered incident investigation."""

    # Prepare evidence first. This also checks whether the incident exists.
    prompts = prepare_ai_investigation(db, incident_id)

    # Register configured providers.
    initialize_providers()

    # Discover models dynamically.
    catalog = ModelCatalog(provider_registry)
    catalog_result = await catalog.refresh_all()

    discovered_models = catalog_result["models"]

    if not discovered_models:
        raise HTTPException(
            status_code=503,
            detail="No models are currently available for investigation."
        )

    # Create the model selector and fallback executor.
    selector = ModelSelector(catalog)
    fallback = FallbackExecutor(selector)

    # Estimate input tokens for model selection.
    combined_prompt = (
        prompts["system_prompt"] + prompts["user_prompt"]
    )

    estimated_input_tokens = max(
        1,
        (len(combined_prompt) + 3) // 4
    )

    # Require text generation.
    # Unknown capability information remains eligible.
    requirements = ModelRequirements(
        required_capabilities={"content_generation"},
        minimum_context_window=16000,
        require_structured_output=False
    )

    request = GenerationRequest(
        system_prompt=prompts["system_prompt"],
        user_prompt=prompts["user_prompt"],
        temperature=0.2,
        max_output_tokens=2048
    )

    try:
        result = await fallback.generate(
            request=request,
            requirements=requirements,
            estimated_input_tokens=estimated_input_tokens,
            result_validator=validate_generation_result
        )

    except FallbackExecutionError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI investigation could not be completed. "
                f"All available model attempts failed "
                f"({len(exc.attempts)} attempts)."
            )
        ) from exc

    # Parse the validated result into the response schema.
    analysis = parse_root_cause_result(result.content)

    return {
        "incident_id": str(incident_id),
        "analysis": analysis.model_dump(),
        "generation": {
            "provider": result.provider,
            "model": result.model,
            "usage": result.usage,
            "finish_reason": result.finish_reason
        },
        "model_discovery": {
            "total_discovered": len(discovered_models),
            "provider_discovery_failures": list(
                catalog_result["failures"].keys()
            )
        }
    }
