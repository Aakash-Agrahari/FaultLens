from langchain_core.messages import AIMessage, ToolMessage

from app.ai.tools.search_logs import search_incident_logs


# Step 1: Simulate an LLM tool-call request.
ai_message = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "search_incident_logs",
            "args": {
                "keyword": "database"
            },
            "id": "call_001",
            "type": "tool_call"
        }
    ]
)


# Step 2: Read the tool request.
tool_call = ai_message.tool_calls[0]

print("Requested tool:", tool_call["name"])
print("Requested arguments:", tool_call["args"])


# Step 3: Execute the requested Python tool.
tool_result = search_incident_logs.invoke(
    tool_call["args"]
)

print("\nTool execution result:")
print(tool_result)


# Step 4: Convert the result into a ToolMessage.
tool_message = ToolMessage(
    content=str(tool_result),
    tool_call_id=tool_call["id"]
)


# Step 5: Display the ToolMessage.
print("\nToolMessage:")
print("Content:", tool_message.content)
print("Tool Call ID:", tool_message.tool_call_id)


# Step 6: Create the conversation history.
conversation = [
    ai_message,
    tool_message
]

print("\nComplete conversation history:")

for message in conversation:
    print("\nMessage type:", message.type)
    print("Content:", message.content)