import os
import datetime as dt
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
creds = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"),
    scopes=SCOPES,
)
calendar_service = build("calendar", "v3", credentials=creds)
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

# Create test event
now = dt.datetime.utcnow()
start = now + dt.timedelta(hours=1)
end = start + dt.timedelta(minutes=30)

event = {
    "summary": "Test Vocca Event",
    "description": "This is a test event to verify Google Calendar integration.",
    "start": {"dateTime": start.isoformat() + "Z", "timeZone": "Europe/Paris"},
    "end": {"dateTime": end.isoformat() + "Z", "timeZone": "Europe/Paris"},
}

# Insert the event
result = calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
print("✅ Event created:", result.get("htmlLink"))
