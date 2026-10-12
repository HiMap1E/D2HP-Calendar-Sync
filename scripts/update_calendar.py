import os
import urllib.request
from pathlib import Path

SOURCE_URL = os.environ["APPS_SCRIPT_URL"]

OUTPUT_FILE = Path("docs/calendar.ics")

MINIMUM_EVENTS = 20


def download_calendar():

    request = urllib.request.Request(
        SOURCE_URL,
        headers={
            "User-Agent": "D2HP-Calendar-Sync/2.3",
            "Accept": "text/calendar, text/plain"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        content = response.read()

    return content


def validate_calendar(content):

    text = content.decode("utf-8-sig")

    if "BEGIN:VCALENDAR" not in text:
        raise ValueError("Invalid ICS header")

    if "END:VCALENDAR" not in text:
        raise ValueError("Invalid ICS footer")

    count = text.count("BEGIN:VEVENT")

    if count < MINIMUM_EVENTS:
        raise ValueError(
            f"Too few events: {count}"
        )

    if "X-D2HP-DEVELOPER:" not in text:
        raise ValueError(
            "Developer metadata missing"
        )

    if "X-D2HP-DISCLAIMER:" not in text:
        raise ValueError(
            "Disclaimer metadata missing"
        )

    if "calendar-about-v1" not in text:
        raise ValueError(
            "About event missing"
        )

    return text


def main():

    content = download_calendar()

    calendar = validate_calendar(content)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    encoded = calendar.encode("utf-8")

    if OUTPUT_FILE.exists():

        previous = OUTPUT_FILE.read_bytes()

        if previous == encoded:
            print("Calendar is already up to date.")
            return

    OUTPUT_FILE.write_bytes(encoded)

    print("Calendar updated successfully.")


if __name__ == "__main__":
    main()
