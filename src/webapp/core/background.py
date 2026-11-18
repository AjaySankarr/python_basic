from datetime import datetime, timezone


def log_event(event: str, details: str):

    timestamp = datetime.now(timezone.utc).isoformat()

    print(
        f"[{timestamp}] "
        f"EVENT: {event} | "
        f"DETAILS: {details}"
    )
    