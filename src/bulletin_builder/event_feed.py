import csv
import io
import json
import urllib.request
from typing import List, Dict


def fetch_events(url: str) -> List[Dict[str, str]]:
    """Fetch events from a JSON or CSV URL.

    Args:
        url: Public URL returning JSON or CSV rows with columns like
            title/description, date, time, image or image_url.

    Returns:
        A list of event dictionaries with ``date``, ``time``, ``description`` and
        ``image_url`` keys.
    """
    with urllib.request.urlopen(url) as resp:
        text = resp.read().decode("utf-8")

    events: List[Dict[str, str]] = []
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("events", []) or data.get("items", [])
        for item in data:
            events.append(
                {
                    "date": item.get("date", ""),
                    "time": item.get("time", ""),
                    "description": item.get("title") or item.get("description", ""),
                    "image_url": item.get("image") or item.get("image_url", ""),
                }
            )
    except json.JSONDecodeError:
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            events.append(
                {
                    "date": row.get("date", ""),
                    "time": row.get("time", ""),
                    "description": row.get("title") or row.get("description", ""),
                    "image_url": row.get("image") or row.get("image_url", ""),
                }
            )
    return [e for e in events if any(e.values())]
