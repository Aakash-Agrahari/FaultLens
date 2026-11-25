from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.ai.prompts.investigation_prompt import investigation_prompt


# Step 1: Create a fake LLM.
# It returns a predefined response instead of calling an API.
fake_model = FakeListChatModel(
    responses=[
        """
        Likely Root Cause:
        Database connection timeout.

        Supporting Evidence:
        Repeated database connection timeout errors.

        Recommended Action:
        Check database connectivity and connection pool settings.
        """
    ]
)


# Step 2: Create an output parser.
output_parser = StrOutputParser()


# Step 3: Connect all components using LCEL.
investigation_chain = (
    investigation_prompt
    | fake_model
    | output_parser
)


# Step 4: Execute the chain.
result = investigation_chain.invoke({
    "incident_details": "Production API returning HTTP 500 errors.",
    "log_evidence": "Database connection timeout occurred repeatedly."
})


# Step 5: Display the result.
print("AI Investigation Result:")
print(result)