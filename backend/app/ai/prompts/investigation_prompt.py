from langchain_core.prompts import ChatPromptTemplate

investigation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an experienced software incident investigator. "
        "Analyze evidence carefully and identify possible root causes."
    ),
    (
        "human",
        """
        Investigate the following software incident.

        Incident Details:
        {incident_details}

        Log Evidence:
        {log_evidence}

        Identify:
        1. Likely root cause
        2. Supporting evidence
        3. Alternative causes
        4. Recommended actions
        """
    )
])