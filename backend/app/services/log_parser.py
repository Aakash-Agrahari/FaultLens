import re

from datetime import datetime, timezone


TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}[ T]"
    r"\d{2}:\d{2}:\d{2}"
    r"(?:[.,]\d{1,6})?"
    r"(?:Z|[+-]\d{2}:?\d{2})?"
)

LEVEL_PATTERN = re.compile(
    r"\b(CRITICAL|FATAL|ERROR|WARN(?:ING)?|INFO|DEBUG)\b",
    re.IGNORECASE
)


def extract_timestamp(line: str):
    match = TIMESTAMP_PATTERN.search(line)

    if not match:
        return None

    timestamp_text = match.group().replace(",", ".")

    if timestamp_text.endswith("Z"):
        timestamp_text = timestamp_text[:-1] + "+00:00"

    try:
        timestamp = datetime.fromisoformat(timestamp_text)

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(
                tzinfo=timezone.utc
            )

        return timestamp

    except ValueError:
        return None


def extract_log_level(line: str) -> str:
    match = LEVEL_PATTERN.search(line)

    if not match:
        return "UNKNOWN"

    level = match.group().upper()

    if level == "FATAL":
        return "CRITICAL"

    if level == "WARN":
        return "WARNING"

    return level

    
def parse_log_file(content: str):
    parsed_entries = []

    for line_number, line in enumerate(
        content.splitlines(),
        start=1
    ):

        if not line.strip():
            continue

        entry = {
            "line_number": line_number,
            "timestamp": extract_timestamp(line),
            "level": extract_log_level(line),
            "message": line.strip()
        }

        parsed_entries.append(entry)

    return parsed_entries            