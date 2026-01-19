#!/usr/bin/env python3
"""Archive existing records and seed new resident-focused demo data."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.db_connection import connect
from app.db_init import init_db

RESIDENT_NAMES = [
    "Avery Cole",
    "Blake Jordan",
    "Casey Morgan",
    "Dakota Reyes",
    "Elliot Turner",
    "Finley Hayes",
    "Gray Parker",
    "Harper Quinn",
    "Indigo Shaw",
    "Jules Carter",
    "Kai Mitchell",
    "Logan Brooks",
    "Marin Scott",
    "Noel Patterson",
    "Oakley Rivera",
    "Parker Bennett",
    "Quinn Lawson",
    "Riley Edwards",
    "Sawyer James",
    "Taylor Cooper",
]

OBJECTIVES = [
    "Complete the next residency milestone.",
    "Stabilize weekly attendance at required sessions.",
    "Build momentum on the individualized progress plan.",
    "Finish the quarterly goal review with the support team.",
    "Strengthen follow-through on the transition checklist.",
]

QUESTIONS = [
    "Which supports are needed before the next review?",
    "Do we need to adjust the current service schedule?",
    "What follow-up is required after the last check-in?",
    "Is transportation support still a blocker this month?",
    "Which milestone needs extra coaching this week?",
]

ITEM_SUMMARY_TEMPLATES = [
    "{name} completed the intake recap.",
    "{name} confirmed the weekly check-in schedule.",
    "{name} updated their goals with the coordinator.",
    "{name} submitted the latest progress notes.",
]

RESIDENT_SUMMARY_TEMPLATES = [
    "{name} is focused on steady progress with weekly check-ins.",
    "{name} is stabilizing routines and tracking milestones.",
    "{name} has momentum on the current support plan.",
    "{name} is closing gaps from the last review cycle.",
]

GOALS = [5, 10, 15, 20, 25]

CHALLENGE_TEMPLATES = [
    "Transportation gaps are slowing follow-through.",
    "Scheduling conflicts with work shifts this month.",
    "Paperwork for benefits renewal is still pending.",
]

OPPORTUNITY_TEMPLATES = [
    "Enroll in the upcoming skills workshop.",
    "Set up peer support check-ins this month.",
    "Coordinate with the case manager on next steps.",
]

MILESTONE_TEMPLATES = [
    "Complete the next progress review by month end.",
    "Finalize the upcoming quarter goals.",
    "Attend the residency milestone meeting.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive existing data and seed new resident demo records.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="Number of residents to seed (default: 20).",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Skip archiving existing records before seeding.",
    )
    return parser.parse_args()


def build_resident_name(index: int) -> str:
    name = RESIDENT_NAMES[index % len(RESIDENT_NAMES)]
    if index < len(RESIDENT_NAMES):
        return name
    return f"{name} {index + 1}"


def build_items(index: int, name: str) -> dict[str, list[str]]:
    summary = [
        ITEM_SUMMARY_TEMPLATES[index % len(ITEM_SUMMARY_TEMPLATES)].format(name=name),
        ITEM_SUMMARY_TEMPLATES[(index + 1) % len(ITEM_SUMMARY_TEMPLATES)].format(name=name),
    ]
    challenges = [
        CHALLENGE_TEMPLATES[index % len(CHALLENGE_TEMPLATES)],
    ]
    opportunities = [
        OPPORTUNITY_TEMPLATES[index % len(OPPORTUNITY_TEMPLATES)],
    ]
    milestones = [
        MILESTONE_TEMPLATES[index % len(MILESTONE_TEMPLATES)],
    ]
    return {
        "summary": summary,
        "challenges": challenges,
        "opportunities": opportunities,
        "milestones": milestones,
    }


def seed_residents(count: int, archive_existing: bool) -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        if archive_existing:
            conn.execute("UPDATE projects SET archived = 1")
        existing_names = {
            row["name"] for row in conn.execute("SELECT name FROM projects").fetchall()
        }
        for index in range(count):
            name = build_resident_name(index)
            if name in existing_names:
                name = f"{name} {index + 1}"
            existing_names.add(name)
            progress = (index * 7 + 18) % 101
            goal = GOALS[index % len(GOALS)]
            objective = OBJECTIVES[index % len(OBJECTIVES)]
            questions = QUESTIONS[index % len(QUESTIONS)]
            summary = RESIDENT_SUMMARY_TEMPLATES[
                index % len(RESIDENT_SUMMARY_TEMPLATES)
            ].format(name=name)
            cursor = conn.execute(
                """
                INSERT INTO projects (name, progress, goal, questions, summary, objective, archived)
                VALUES (?, ?, ?, ?, ?, ?, 0)
                """,
                (name, progress, goal, questions, summary, objective),
            )
            project_id = cursor.lastrowid
            items = build_items(index, name)
            for section, entries in items.items():
                for content in entries:
                    conn.execute(
                        """
                        INSERT INTO items (project_id, section, content, created_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (project_id, section, content, now),
                    )
        conn.commit()


def main() -> int:
    args = parse_args()
    if args.count < 1:
        raise ValueError("--count must be at least 1")
    seed_residents(args.count, archive_existing=not args.keep_existing)
    print(f"Seeded {args.count} residents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
