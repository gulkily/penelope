#!/usr/bin/env python3
"""Seed additional demo data for presentations."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.db_connection import connect
from app.db_init import init_db

DEMO_PROJECTS: list[dict[str, object]] = [
    {
        "name": "Project Atlas",
        "progress": 78,
        "goal": 25,
        "resident_summary": (
            "Working on onboarding improvements and activation step-2 experiments, "
            "with focus on shortening the first-run flow and support checklist."
        ),
        "objective": "Reduce onboarding time to under 3 minutes by quarter end.",
        "questions": "Do we need a walkthrough for enterprise users?",
        "archived": 0,
        "items": {
            "summary": [
                "Revamped first-run checklist shipped.",
                "Support tickets dropped 12% week-over-week.",
            ],
            "challenges": [
                "Activation funnel still drops at step 2.",
            ],
            "opportunities": [
                "Test pre-filled templates for new accounts.",
            ],
            "milestones": [
                "Finalize onboarding playbook by Friday.",
            ],
        },
    },
    {
        "name": "Project Meridian",
        "progress": 52,
        "goal": 40,
        "resident_summary": (
            "Shipping weekly insights to key accounts while stabilizing peak-hour "
            "performance and refining the reporting pipeline."
        ),
        "objective": "Ship weekly insights for 10 accounts for 6 straight weeks.",
        "questions": "Which accounts need custom dashboards?",
        "archived": 0,
        "items": {
            "summary": [
                "Insight cards now render for all active accounts.",
            ],
            "challenges": [
                "Latency spikes during peak hours.",
            ],
            "opportunities": [
                "Precompute nightly summaries to reduce load.",
            ],
            "milestones": [
                "Pilot weekly emails with 3 accounts.",
            ],
        },
    },
    {
        "name": "Project Lantern",
        "progress": 34,
        "goal": 20,
        "resident_summary": (
            "Focusing on retention drivers, survey feedback, and a win-back plan to "
            "improve SMB outcomes."
        ),
        "objective": "Cut churn by 20% in the SMB segment over the next 90 days.",
        "questions": "Do we need a win-back campaign?",
        "archived": 0,
        "items": {
            "summary": [
                "Retention survey drafted.",
            ],
            "challenges": [
                "Limited data on churn reasons.",
            ],
            "opportunities": [
                "Offer proactive success check-ins.",
            ],
            "milestones": [
                "Launch churn survey next week.",
            ],
        },
    },
    {
        "name": "Project Nimbus",
        "progress": 61,
        "goal": 30,
        "resident_summary": (
            "Driving reliability improvements, tuning autoscaling, and preparing "
            "the launch runbook for core services."
        ),
        "objective": "Hit 95% uptime for Q4 launch across 3 core services.",
        "questions": "Which services need redundancy first?",
        "archived": 0,
        "items": {
            "summary": [
                "Load testing dashboard is live.",
            ],
            "challenges": [
                "Autoscaling thresholds need tuning.",
            ],
            "opportunities": [
                "Introduce regional failover.",
            ],
            "milestones": [
                "Complete chaos testing plan.",
            ],
        },
    },
    {
        "name": "Project Quartz",
        "progress": 19,
        "goal": 15,
        "resident_summary": (
            "Building the partner pipeline, refining outreach messaging, and "
            "scheduling the first round of demos."
        ),
        "objective": "Recruit 5 new design partners by month end.",
        "questions": "Who owns partner outreach?",
        "archived": 0,
        "items": {
            "summary": [
                "Prospect list refined.",
            ],
            "challenges": [
                "Need sharper positioning for outreach.",
            ],
            "opportunities": [
                "Bundle pilot pricing with analytics.",
            ],
            "milestones": [
                "Book 3 partner demos by month-end.",
            ],
        },
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed additional demo data for the North Star dashboard.",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Insert demo projects even if a project with the same name exists.",
    )
    return parser.parse_args()


def seed_demo_projects(allow_duplicates: bool) -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    year = datetime.now(timezone.utc).year
    with connect() as conn:
        existing = set()
        if not allow_duplicates:
            existing = {
                row["name"] for row in conn.execute("SELECT name FROM projects").fetchall()
            }

        for project in DEMO_PROJECTS:
            name = str(project["name"])
            if not allow_duplicates and name in existing:
                continue
            cursor = conn.execute(
                """
                INSERT INTO projects (name, progress, goal, questions, summary, objective, archived)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    int(project["progress"]),
                    int(project["goal"]),
                    str(project["questions"]),
                    str(project["resident_summary"]),
                    str(project["objective"]),
                    int(project["archived"]),
                ),
            )
            project_id = cursor.lastrowid
            items = project.get("items", {})
            for section, entries in items.items():
                for content in entries:
                    conn.execute(
                        """
                        INSERT INTO items (project_id, section, content, created_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (project_id, section, str(content), now),
                    )
            for recorded_at, progress_value in build_progress_history(
                int(project["progress"]),
                year,
            ):
                conn.execute(
                    """
                    INSERT INTO progress_history (project_id, progress, recorded_at)
                    VALUES (?, ?, ?)
                    """,
                    (project_id, progress_value, recorded_at),
                )
        conn.commit()


def build_progress_history(progress: int, year: int) -> list[tuple[str, int]]:
    anchors = [1, 8, 15, 22, 31]
    steps = [0.2, 0.4, 0.6, 0.8, 1.0]
    values = [max(0, int(round(progress * step))) for step in steps]
    values[-1] = int(progress)
    for index in range(1, len(values)):
        if values[index] < values[index - 1]:
            values[index] = values[index - 1]
    entries: list[tuple[str, int]] = []
    for day, value in zip(anchors, values):
        timestamp = datetime(year, 1, day, 12, 0, tzinfo=timezone.utc).isoformat()
        entries.append((timestamp, value))
    return entries


def main() -> int:
    args = parse_args()
    seed_demo_projects(args.allow_duplicates)
    print("Demo data added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
