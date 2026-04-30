import csv
import json
import os
import re
from datetime import datetime, timedelta
from functools import reduce


def current_timestamp():
    return datetime.now().isoformat(timespec='seconds')


def parse_datetime(value):
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except Exception:
        raise ValueError(f"Invalid datetime value: {value}")


def format_duration(seconds):
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{sec}s")
    return ' '.join(parts)


def generate_ticket_id(existing_ids, prefix='TKT'):
    existing_ints = [int(re.sub(r'[^0-9]', '', ticket_id) or '0') for ticket_id in existing_ids]
    next_number = max(existing_ints, default=0) + 1
    return f"{prefix}-{next_number:03d}"


def safe_input(prompt, required=True):
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("Value cannot be empty. Please try again.")


def load_json(filepath, default=None):
    if default is None:
        default = []
    if not os.path.exists(filepath):
        return default
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def write_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def append_text(filepath, text):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(text + '\n')


def csv_backup(filepath, header, rows):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def reduce_tickets(tickets, key):
    return reduce(lambda acc, ticket: acc.__setitem__(ticket[key], acc.get(ticket[key], 0) + 1) or acc, tickets, {})
