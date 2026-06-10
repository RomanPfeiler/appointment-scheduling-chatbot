from datetime import datetime

from pydantic import BaseModel, model_validator


class Topic(BaseModel):
    topic_id: str
    topic_name: str


class ContactMedium(BaseModel):
    contact_medium_id: str
    contact_medium_name: str


class TimeSlot(BaseModel):
    datetime_start: datetime
    datetime_end: datetime

    @model_validator(mode="after")
    def start_before_end(self) -> "TimeSlot":
        if self.datetime_start >= self.datetime_end:
            raise ValueError(
                f"datetime_start ({self.datetime_start}) must be before "
                f"datetime_end ({self.datetime_end})"
            )
        return self

    def to_iso(self) -> dict[str, str]:
        """Return both datetimes as ISO 8601 strings with timezone offset."""
        return {
            "datetime_start": self.datetime_start.isoformat(),
            "datetime_end": self.datetime_end.isoformat(),
        }


class AvailabilityRequest(BaseModel):
    topic_id: str
    contact_medium_id: str
    start_datetime: datetime
    end_datetime: datetime


class BookingResult(BaseModel):
    status: str
    booking_id: str
    topic_name: str
    contact_medium_name: str
    datetime_start: datetime
    datetime_end: datetime
