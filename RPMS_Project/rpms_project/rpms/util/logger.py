from datetime import datetime
from pathlib import Path

def log_activity(message):
    path = Path('activity_log.txt')
    with path.open('a', encoding='utf-8') as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {message}\n")
