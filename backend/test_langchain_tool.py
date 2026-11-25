from langchain_core.tools import tool


# Sample incident logs for learning.
sample_logs = [
    "Database connection timeout occurred.",
    "API returned HTTP 500.",
    "Database connection pool exhausted.",
    "User authentication successful.",
    "Connection to PostgreSQL failed."
]


# Convert a Python function into a LangChain tool.
@tool
def search_incident_logs(keyword: str) -> list[str]:
    """
    Search incident logs using a keyword.

    Args:
        keyword: The keyword to search for in incident logs.
    """

    matching_logs = [
        log for log in sample_logs
        if keyword.lower() in log.lower()
    ]

    return matching_logs


# Inspect the tool.
print("Tool name:", search_incident_logs.name)
print("Tool description:", search_incident_logs.description)
print("Tool arguments:", search_incident_logs.args)


# Execute the tool directly.
result = search_incident_logs.invoke({
    "keyword": "database"
})

print("\nMatching logs:")
for log in result:
    print("-", log)