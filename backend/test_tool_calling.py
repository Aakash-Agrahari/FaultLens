from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from app.ai.tools.search_logs import search_incident_logs


# Step 1: Simulate an LLM deciding to call a tool.
def fake_llm_decision(input_data):

    print("LLM received:", input_data["question"])

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


# Step 2: Wrap the simulated LLM as a Runnable.
fake_llm = RunnableLambda(fake_llm_decision)


# Step 3: Ask the simulated LLM a question.
ai_response = fake_llm.invoke({
    "question": "Why is my production API returning HTTP 500 errors?"
})


# Step 4: Check whether the LLM requested a tool.
if ai_response.tool_calls:

    for tool_call in ai_response.tool_calls:

        print("\nLLM requested tool:", tool_call["name"])
        print("Arguments:", tool_call["args"])

        # Step 5: Execute the requested tool.
        if tool_call["name"] == "search_incident_logs":

            tool_result = search_incident_logs.invoke(
                tool_call["args"]
            )

            print("\nTool execution result:")

            for log in tool_result:
                print("-", log)

else:
    print("LLM returned:", ai_response.content)