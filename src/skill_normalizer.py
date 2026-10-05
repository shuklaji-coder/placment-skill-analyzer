"""Skill normalisation engine.

Converts each student's raw free-text evidence (Technical_Skills, Projects,
Internships, Certifications) into evidence counts per master skill:
    mentions      -> skill named in the Technical_Skills column
    project_hits  -> skill keywords found inside project descriptions
    intern_hits   -> skill keywords found inside internship descriptions
    cert_hits     -> skill keywords found inside certification descriptions

The evidence counts are later converted to scores by student_scoring.py.
"""
import re

import pandas as pd

from .config import MASTER_SKILLS, SKILL_KEYWORDS


def _compile_patterns():
    compiled = {}
    for skill, patterns in SKILL_KEYWORDS.items():
        compiled[skill] = [re.compile(p, re.IGNORECASE) for p in patterns]
    return compiled


_COMPILED = _compile_patterns()


def _hit_count(text, patterns):
    """Return number of distinct patterns matched in a text (0..len(patterns))."""
    if not text or text in ("NA", "None", "nan"):
        return 0
    count = 0
    for pat in patterns:
        if pat.search(text):
            count += 1
    return count


def evidence_for_student(row):
    """Compute evidence counts for one student row.

    Returns dict {skill: {"mentions": bool, "project_hits": int,
                          "intern_hits": int, "cert_hits": int}}
    """
    skills_text = str(row.get("Technical_Skills", ""))
    projects_text = str(row.get("Projects", ""))
    intern_text = str(row.get("Internships", ""))
    cert_text = str(row.get("Certifications", ""))

    result = {}
    for skill in MASTER_SKILLS:
        patterns = _COMPILED[skill]
        result[skill] = {
            "mentions": _hit_count(skills_text, patterns) > 0,
            "project_hits": _hit_count(projects_text, patterns),
            "intern_hits": _hit_count(intern_text, patterns),
            "cert_hits": _hit_count(cert_text, patterns),
        }
    return result


def build_evidence_frame(students_df):
    """Build an evidence-count DataFrame (rows = students, cols = master skills).

    Each master skill contributes four columns suffixed with the evidence type.
    """
    records = []
    for _, row in students_df.iterrows():
        ev = evidence_for_student(row)
        record = {"Roll_No": row["Roll_No"], "Student_Name": row["Student_Name"]}
        for skill in MASTER_SKILLS:
            e = ev[skill]
            record[f"{skill}::mentions"] = int(e["mentions"])
            record[f"{skill}::project_hits"] = e["project_hits"]
            record[f"{skill}::intern_hits"] = e["intern_hits"]
            record[f"{skill}::cert_hits"] = e["cert_hits"]
        records.append(record)

    return pd.DataFrame(records)
