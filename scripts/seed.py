#!/usr/bin/env python3
import json
import sys
import urllib.request
from datetime import date, timedelta

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:3000"

SUBJECTS = [
    {
        "name": "Operating Systems",
        "code": "CS301",
        "color": "#0ea5e9",
        "exam_in": 11,
        "topics": [
            ("Processes and threads", "done", 2, 2),
            ("CPU scheduling algorithms", "done", 3, 3),
            ("Synchronisation and semaphores", "in_progress", 4, 4),
            ("Deadlocks", "todo", 3, 2.5),
            ("Paging and TLBs", "todo", 4, 3),
            ("File systems", "todo", 2, 2),
        ],
    },
    {
        "name": "Database Systems",
        "code": "CS305",
        "color": "#10b981",
        "exam_in": 18,
        "topics": [
            ("ER modelling", "done", 1, 1.5),
            ("Relational algebra", "done", 3, 2),
            ("SQL joins and subqueries", "done", 2, 2),
            ("Normalisation up to BCNF", "in_progress", 4, 3),
            ("Transactions and ACID", "todo", 3, 2),
            ("B+ tree indexing", "todo", 5, 3.5),
        ],
    },
    {
        "name": "Discrete Mathematics",
        "code": "MA201",
        "color": "#f59e0b",
        "exam_in": 25,
        "topics": [
            ("Propositional logic", "done", 2, 2),
            ("Proof techniques", "in_progress", 3, 3),
            ("Graph theory", "todo", 4, 4),
            ("Recurrence relations", "todo", 5, 3),
        ],
    },
    {
        "name": "Computer Networks",
        "code": "CS302",
        "color": "#8b5cf6",
        "exam_in": 32,
        "topics": [
            ("OSI and TCP/IP layers", "done", 1, 1),
            ("Subnetting", "todo", 3, 2),
            ("TCP congestion control", "todo", 5, 3),
            ("Routing protocols", "todo", 4, 3),
        ],
    },
]


def post(path, payload):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.load(res)


def main():
    for s in SUBJECTS:
        subject = post(
            "/api/subjects",
            {
                "name": s["name"],
                "code": s["code"],
                "color": s["color"],
                "exam_date": (date.today() + timedelta(days=s["exam_in"])).isoformat(),
            },
        )
        for title, status, difficulty, hours in s["topics"]:
            post(
                "/api/topics",
                {
                    "subject_id": subject["id"],
                    "title": title,
                    "status": status,
                    "difficulty": difficulty,
                    "estimated_hours": hours,
                },
            )
        print(f"seeded {s['name']} ({len(s['topics'])} topics)")


if __name__ == "__main__":
    main()
