from app.ai.prompts.investigation_prompt import investigation_prompt


# Supply input variables to the prompt template.
prompt_value = investigation_prompt.invoke({
    "incident_details": "Production API returning HTTP 500 errors.",
    "log_evidence": "Database connection timeout occurred repeatedly."
})


# Convert ChatPromptValue into individual messages.
messages = prompt_value.to_messages()


for message in messages:
    print("\nRole:", message.type)
    print("Content:", message.content)