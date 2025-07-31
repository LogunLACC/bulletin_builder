import csv
import io
import json
import urllib.request
import os
import tempfile
from typing import List, Dict
from datetime import datetime, date, timedelta
import re

from .image_utils import optimize_image


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


def events_to_blocks(events: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Convert raw event dictionaries into standard bulletin blocks.

    Each returned block is guaranteed to have ``date``, ``time``, ``description``
    and ``image_url`` keys so templates can render them without additional
    checks.
    """
    blocks: List[Dict[str, str]] = []
    for ev in events:
        blocks.append(
            {
                "date": (ev.get("date") or "").strip(),
                "time": (ev.get("time") or "").strip(),
                "description": (ev.get("description") or ev.get("title") or "").strip(),
                "image_url": (ev.get("image_url") or ev.get("image") or "").strip(),
            }
        )
    return blocks


def process_event_images(
    events: List[Dict[str, str]],
    dest_dir: str = "assets",
    max_width: int = 800,
    ratio: tuple[int, int] = (4, 3),
) -> None:
    """Download and standardize event images in place."""
    for ev in events:
        url = ev.get("image_url", "")
        if not url:
            continue
        try:
            if url.startswith("http://") or url.startswith("https://"):
                ext = os.path.splitext(url)[1] or ".jpg"
                fd, tmp_path = tempfile.mkstemp(suffix=ext)
                os.close(fd)
                urllib.request.urlretrieve(url, tmp_path)
                local = tmp_path
            else:
                local = url
            opt_path = optimize_image(
                local, dest_dir=dest_dir, max_width=max_width, ratio=ratio
            )
            ev["image_url"] = opt_path
        except Exception:
            continue


WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def _parse_date(value: str, default_year: int) -> date | None:
    if not value:
        return None
    clean = value.split("-")[0].strip()
    patterns = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%A, %B %d, %Y",
        "%A, %B %d",
        "%B %d",
        "%b %d",
    ]
    for fmt in patterns:
        try:
            dt = datetime.strptime(clean, fmt)
            if "%Y" not in fmt:
                dt = dt.replace(year=default_year)
            return dt.date()
        except ValueError:
            continue
    return None


def _parse_recurring_day(text: str) -> str | None:
    if not text:
        return None
    lower = text.strip().lower()
    if re.search(r"every\s+day", lower):
        return "daily"
    for day in WEEKDAYS:
        if day.lower() in lower and not any(ch.isdigit() for ch in lower):
            return day
    return None


def expand_recurring_event(
    event: Dict[str, str], bulletin_date: str = "", weeks: int = 4
) -> List[Dict[str, str]]:
    day = _parse_recurring_day(event.get("date", ""))
    if not day:
        return [event]

    base = _parse_date(bulletin_date, datetime.today().year) or date.today()

    occurrences: List[Dict[str, str]] = []
    if day == "daily":
        start = base
        for i in range(weeks * 7):
            dt = start + timedelta(days=i)
            ev = event.copy()
            ev["date"] = dt.strftime("%A, %B %d, %Y")
            occurrences.append(ev)
    else:
        idx = WEEKDAYS.index(day)
        start = base + timedelta((idx - base.weekday()) % 7)
        for i in range(weeks):
            dt = start + timedelta(days=i * 7)
            ev = event.copy()
            ev["date"] = dt.strftime("%A, %B %d, %Y")
            occurrences.append(ev)
    return occurrences


def expand_recurring_events(
    events: List[Dict[str, str]], bulletin_date: str = "", weeks: int = 4
) -> List[Dict[str, str]]:
    expanded: List[Dict[str, str]] = []
    for ev in events:
        expanded.extend(expand_recurring_event(ev, bulletin_date, weeks))
    return expanded

