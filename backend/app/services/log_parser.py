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

# Recognizes the beginning of a new log entry.
LOG_START_PATTERN = re.compile(
    r"^\s*(?:"
    + TIMESTAMP_PATTERN.pattern
    + r"|(?:\[[^\]]+\]\s*)?(?:CRITICAL|FATAL|ERROR|WARN(?:ING)?|INFO|DEBUG)\b"
    + r")",
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
            timestamp = timestamp.replace(tzinfo=timezone.utc)

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
    current_entry = None

    for line_number, line in enumerate(content.splitlines(), start=1):

        if not line.strip():
            continue

        if LOG_START_PATTERN.search(line):

            if current_entry is not None:
                parsed_entries.append(current_entry)

            current_entry = {
                "line_number": line_number,
                "timestamp": extract_timestamp(line),
                "level": extract_log_level(line),
                "message": line.strip()
            }

        else:

            if current_entry is None:
                current_entry = {
                    "line_number": line_number,
                    "timestamp": None,
                    "level": "UNKNOWN",
                    "message": line.strip()
                }

            else:
                current_entry["message"] += "\n" + line.rstrip()

    if current_entry is not None:
        parsed_entries.append(current_entry)

    return parsed_entries
