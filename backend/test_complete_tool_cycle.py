from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage
)
from langchain_core.runnables import RunnableLambda

from app.ai.tools.search_logs import search_incident_logs


# Step 1: Simulate an LLM.
# First it requests a tool.
# After receiving the tool result, it generates a final answer.

def fake_llm(messages):

    # Check whether a tool result has been received.
    tool_results = [
        message for message in messages
        if isinstance(message, ToolMessage)
    ]

    if not tool_results:

        print("LLM: I need to search the incident logs.")

        return AIMessage(
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

    # Generate a simulated final response.
    evidence = tool_results[-1].content

    return AIMessage(
        content=(
            "Based on the retrieved evidence, the production API "
            "may be failing because of database connectivity issues.\n\n"
            f"Supporting evidence: {evidence}\n\n"
            "Recommended action: Check database connectivity "
            "and connection pool settings."
        )
    )


# Step 2: Wrap the simulated LLM.
llm = RunnableLambda(fake_llm)


# Step 3: Create conversation history.
messages = [
    HumanMessage(
        content="Why is my production API returning HTTP 500 errors?"
    )
]


# Step 4: First LLM invocation.
ai_response = llm.invoke(messages)

messages.append(ai_response)


# Step 5: Execute requested tools.
for tool_call in ai_response.tool_calls:

    if tool_call["name"] == "search_incident_logs":

        print("\nExecuting:", tool_call["name"])

        result = search_incident_logs.invoke(
            tool_call["args"]
        )

        # Return tool result to the conversation.
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        )

        messages.append(tool_message)


# Step 6: Send the tool result back to the LLM.
final_response = llm.invoke(messages)

messages.append(final_response)


# Step 7: Display the final response.
print("\nFINAL INVESTIGATION RESULT:")
print(final_response.content)


# Step 8: Display conversation history.
print("\nCONVERSATION HISTORY:")

for message in messages:
    print("\nMessage type:", message.type)
    print("Content:", message.content)