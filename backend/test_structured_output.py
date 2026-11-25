from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.schemas.ai_investigation import RootCauseAnalysis


# Step 1: Connect the existing Pydantic schema to LangChain.
parser = PydanticOutputParser(
    pydantic_object=RootCauseAnalysis
)


# Step 2: Create a prompt template.
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an experienced software incident investigator. "
        "Analyze the evidence and return a structured investigation."
    ),
    (
        "human",
        """
        Investigate this incident.

        Incident:
        {incident_details}

        Evidence:
        {log_evidence}

        Follow these output instructions:
        {format_instructions}
        """
    )
])


# Step 3: Supply the parser's formatting instructions.
prompt = prompt.partial(
    format_instructions=parser.get_format_instructions()
)


# Step 4: Simulate an LLM response.
fake_model = FakeListChatModel(
    responses=[
        """
        {
            "likely_root_cause": "Database connection timeout",
            "confidence": 0.9,
            "explanation": "Repeated database connection failures caused API errors.",
            "supporting_evidence": [
                "Database connection timeout occurred repeatedly."
            ],
            "alternative_causes": [
                "Database connection pool exhaustion"
            ],
            "recommended_actions": [
                "Check database connectivity",
                "Inspect connection pool settings"
            ],
            "missing_information": [
                "Database connection pool metrics"
            ]
        }
        """
    ]
)


# Step 5: Build the complete LCEL chain.
investigation_chain = (
    prompt
    | fake_model
    | parser
)


# Step 6: Execute the chain.
result = investigation_chain.invoke({
    "incident_details": "Production API returning HTTP 500 errors.",
    "log_evidence": "Database connection timeout occurred repeatedly."
})


# Step 7: Display the structured result.
print("Structured Investigation Result:")
print(result.model_dump())

print("\nRoot Cause:", result.likely_root_cause)
print("Confidence:", result.confidence)
print("Recommended Actions:", result.recommended_actions)