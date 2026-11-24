from app.ai.prompts.investigation_prompt import investigation_prompt


messages = investigation_prompt.format_messages(
    incident_details="Production API returning HTTP 500 errors.",
    log_evidence="Database connection timeout occurred repeatedly."
)

for message in messages:
    print(f"\nRole: {message.type}")
    print(f"Content: {message.content}")