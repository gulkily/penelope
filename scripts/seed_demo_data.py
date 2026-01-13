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
        "objective": "Reduce onboarding time to under 3 minutes.",
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
        "objective": "Ship weekly insights for the top 10 accounts.",
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
        "objective": "Cut churn by 20% in SMB segment.",
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
        "objective": "Hit 95% uptime for Q4 launch.",
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
        "objective": "Recruit 5 new design partners.",
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
                INSERT INTO projects (name, progress, questions, objective, archived)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    int(project["progress"]),
                    str(project["questions"]),
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
        conn.commit()


def main() -> int:
    args = parse_args()
    seed_demo_projects(args.allow_duplicates)
    print("Demo data added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
