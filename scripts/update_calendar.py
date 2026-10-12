import os
import urllib.request
from pathlib import Path

SOURCE_URL = os.environ["APPS_SCRIPT_URL"]
OUTPUT_FILE = Path("docs/calendar.ics")

MIN_EVENTS = 20


def download_calendar():
    request = urllib.request.Request(
        SOURCE_URL,
        headers={
            "User-Agent": "D2HP-Calendar-Sync/2.3",
            "Accept": "text/calendar, text/plain",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=60,
    ) as response:
        content = response.read()

    return content.decode("utf-8-sig")


def validate_calendar(text):
    # Normalise line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if not text.startswith("BEGIN:VCALENDAR\n"):
        raise ValueError("Invalid iCalendar header")

    if not text.rstrip().endswith("END:VCALENDAR"):
        raise ValueError("Invalid iCalendar footer")

    event_count = text.count("BEGIN:VEVENT")

    if event_count < MIN_EVENTS:
        raise ValueError(
            f"Too few calendar events: {event_count}"
        )

    required_fields = [
        "VERSION:2.0",
        "X-D2HP-DEVELOPER:",
        "X-D2HP-COPYRIGHT:",
        "X-D2HP-DISCLAIMER:",
        "calendar-about-v1",
    ]

    # Unfold logical iCalendar lines for validation.
    unfolded = text.replace("\n ", "").replace("\n\t", "")

    for field in required_fields:
        if field not in unfolded:
            raise ValueError(f"Missing field: {field}")

    if "BEGIN:VALARM" in unfolded:
        raise ValueError("Unexpected calendar alarm")

    print(f"Validated {event_count} events.")

    # Convert to RFC 5545 CRLF line endings.
    return text.rstrip("\n").replace("\n", "\r\n") + "\r\n"


def main():
    print("Downloading calendar from Apps Script...")

    content = download_calendar()
    calendar = validate_calendar(content)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    new_content = calendar.encode("utf-8")

    if (
        OUTPUT_FILE.exists()
        and OUTPUT_FILE.read_bytes() == new_content
    ):
        print("Calendar unchanged.")
        return

    OUTPUT_FILE.write_bytes(new_content)

    print(f"Updated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
