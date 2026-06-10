from zoneinfo import ZoneInfo

TIMEZONE: ZoneInfo = ZoneInfo("Europe/Zurich")

BUSINESS_HOURS_START: int = 8   # 08:00 local time
BUSINESS_HOURS_END: int = 17    # 17:00 local time

LEAD_TIME_HOURS: int = 24               # Earliest bookable slot = now + 24h
DEFAULT_SLOT_DURATION_MINUTES: int = 60 # All topics use 60-min slots for MVP
MAX_AVAILABILITY_WINDOW_DAYS: int = 3   # Max days per single check_availability call
SCHEDULING_HORIZON_DAYS: int = 21       # How far ahead slots are generated
