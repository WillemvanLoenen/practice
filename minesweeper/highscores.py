import json
import os

HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscores.json")
MAX_ENTRIES = 5

RANKED_DIFFICULTIES = ["Beginner", "Intermediate", "Expert"]


def load_highscores() -> dict:
    """Load the highscore table from disk, creating empty lists for any
    difficulty that doesn't have entries yet (e.g. first run)."""
    data = {}
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = {}

    for level in RANKED_DIFFICULTIES:
        data.setdefault(level, [])
    return data


def save_highscores(data: dict) -> None:
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def qualifies(data: dict, level: str, time_seconds: int) -> bool:
    """True if time_seconds would make it into the top MAX_ENTRIES for this level."""
    scores = data.get(level, [])
    if len(scores) < MAX_ENTRIES:
        return True
    return time_seconds < max(entry["time"] for entry in scores)


def add_score(data: dict, level: str, name: str, time_seconds: int) -> None:
    scores = data.setdefault(level, [])
    scores.append({"name": name, "time": time_seconds})
    scores.sort(key=lambda entry: entry["time"])
    del scores[MAX_ENTRIES:]  # keep only the best MAX_ENTRIES
    save_highscores(data)
