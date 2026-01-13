import random
import uuid

PROJECT_WORDS = [
    "Atlas",
    "Beacon",
    "Cedar",
    "Horizon",
    "Nimbus",
    "Orion",
    "Summit",
    "Aurora",
    "Harbor",
    "Sierra",
]


def unique_project_name() -> str:
    word = random.choice(PROJECT_WORDS)
    token = uuid.uuid4().hex[:8].upper()
    return f"Project {word} {token}"
