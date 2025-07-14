"""
calendar_helper.py – Google Calendar integration
"""
from __future__ import annotations
import os, re, datetime as dt

from loguru import logger
from google.oauth2 import service_account
from googleapiclient.discovery import build

from pipecat.frames.frames import Frame, LLMTextFrame
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection

# ─────────── Google Calendar auth ───────────
SCOPES = ["https://www.googleapis.com/auth/calendar"]
creds = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"), scopes=SCOPES
)
calendar_service = build("calendar", "v3", credentials=creds)
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

# Confirmation pattern – full match
FULL_CONFIRMATION_PATTERN = re.compile(
    r"le créneau est réservé le (\d{1,2})/(\d{1,2})/(\d{4}) à (\d{1,2})h(\d{2})",
    flags=re.I
)


class CalendarProcessor(FrameProcessor):
    def __init__(self):
        super().__init__()
        self._assistant_buffer = ""

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if (
            direction == FrameDirection.DOWNSTREAM
            and isinstance(frame, LLMTextFrame)
        ):
            # Accumulate assistant text across streaming chunks
            self._assistant_buffer += frame.text
            txt = self._assistant_buffer.lower().strip()

            logger.debug(f"[CalendarProcessor] Accumulated buffer: {txt!r}")

            match = FULL_CONFIRMATION_PATTERN.search(txt)
            if match:
                logger.info(f"[CalendarProcessor] Detected full confirmation sentence.")
                self._assistant_buffer = ""  # Clear buffer

                try:
                    day, month, year, hour, minute = map(int, match.groups())
                    start = dt.datetime(year, month, day, hour, minute)
                    end   = start + dt.timedelta(minutes=30)

                    event = {
                        "summary": "Rendez-vous Vocca",
                        "description": "Réservé via chatbot Vocca",
                        "start": {"dateTime": start.isoformat(), "timeZone": "Europe/Paris"},
                        "end":   {"dateTime": end.isoformat(), "timeZone": "Europe/Paris"},
                    }

                    calendar_service.events().insert(
                        calendarId=CALENDAR_ID, body=event
                    ).execute()
                    logger.info("🗓️  Event successfully added to Google Calendar.")
                except Exception as e:
                    logger.error(f"Google Calendar error: {e}")

        await self.push_frame(frame, direction)
