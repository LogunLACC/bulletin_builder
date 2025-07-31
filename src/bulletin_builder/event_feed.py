import csv
import io
import json
import urllib.request
import os
import tempfile
import calendar
import re
from datetime import datetime, timedelta, time
from typing import List, Dict, Iterable

from .image_utils import optimize_image


def _normalize_tags(raw: Iterable | str | None) -> list[str]:
    """Return a list of lowercase tags from a variety of inputs."""
    if not raw:
        return []
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.split(',')]
    else:
        try:
            parts = [str(p).strip() for p in raw]
        except TypeError:
            parts = []
    return [p.lower() for p in parts if p]


def fetch_events(url: str) -> List[Dict[str, str]]:
    """Fetch events from a JSON or CSV URL.

    Args:
        url: Public URL returning JSON or CSV rows with columns like
            title/description, date, time, image or image_url.

    Returns:
        A list of event dictionaries with ``date``, ``time``, ``description``,
        ``image_url``, ``link`` and ``map_link`` keys.
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
                    "tags": _normalize_tags(item.get("tags") or item.get("categories") or item.get("labels") or item.get("tag")),
                    "link": item.get("link") or item.get("url", ""),
                    "map_link": item.get("map") or item.get("map_link", ""),
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
                    "tags": _normalize_tags(row.get("tags") or row.get("categories") or row.get("labels") or row.get("tag")),
                    "link": row.get("link") or row.get("url", ""),
                    "map_link": row.get("map") or row.get("map_link", ""),
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
                "tags": _normalize_tags(ev.get("tags")),
                "link": (ev.get("link") or ev.get("url") or "").strip(),
                "map_link": (ev.get("map_link") or ev.get("map") or "").strip(),
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


def expand_recurring_events(events: List[Dict[str, str]], days: int = 60) -> List[Dict[str, str]]:
    """Expand simple weekly recurring events into individual occurrences.

    Events may provide a ``recurrence`` or ``rrule`` field in the form
    ``"weekly:Monday"``. Each occurrence within ``days`` days from today is
    returned as a separate event dictionary with the ``date`` field set.
    Past events are automatically filtered out.
    """
    start = datetime.utcnow().date()
    end = start + timedelta(days=days)
    expanded: List[Dict[str, str]] = []

    for ev in events:
        rule = ev.get("recurrence") or ev.get("rrule")
        if rule:
            m = re.match(r"weekly:(\w+)", str(rule), re.IGNORECASE)
            if m:
                weekday = m.group(1).capitalize()
                if weekday in calendar.day_name:
                    idx = list(calendar.day_name).index(weekday)
                    current = start
                    while current <= end:
                        if current.weekday() == idx:
                            nev = ev.copy()
                            nev["date"] = current.isoformat()
                            expanded.append(nev)
                        current += timedelta(days=1)
                continue
        # If no recurrence rule, include future-dated events only
        date_str = ev.get("date")
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str)
                if dt.date() < start:
                    continue
            except Exception:
                pass
        expanded.append(ev)

    return expanded


def _parse_time(value: str) -> time | None:
    """Parse a time string to ``datetime.time`` if possible."""
    if not value:
        return None
    value = value.strip().lower().replace(".", "")
    patterns = [
        "%I:%M %p",
        "%I %p",
        "%H:%M",
        "%H",
    ]
    for fmt in patterns:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return None


def _parse_time_range(value: str) -> tuple[time | None, time | None]:
    """Return (start, end) times from a value like '9am-10am'."""
    if not value:
        return None, None
    parts = re.split(r"\s*-\s*|\s+to\s+", value, maxsplit=1)
    if len(parts) == 2:
        start = _parse_time(parts[0])
        end = _parse_time(parts[1])
    else:
        start = _parse_time(value)
        end = None
    return start, end


def detect_conflicts(events: List[Dict[str, str]]) -> List[tuple[Dict[str, str], Dict[str, str]]]:
    """Return pairs of events that overlap in time on the same date."""
    parsed = []
    for ev in events:
        start, end = _parse_time_range(ev.get("time", ""))
        if ev.get("date") and start:
            if end is None:
                end_dt = datetime.combine(datetime.today(), start) + timedelta(hours=1)
                end = end_dt.time()
            parsed.append((ev.get("date"), start, end, ev))

    parsed.sort(key=lambda t: (t[0], t[1]))
    conflicts = []
    for i in range(len(parsed) - 1):
        d1, s1, e1, ev1 = parsed[i]
        d2, s2, e2, ev2 = parsed[i + 1]
        if d1 == d2 and s2 < e1:
            conflicts.append((ev1, ev2))
    return conflicts

