"""Student skill scoring.

Converts the evidence counts produced by skill_normalizer into evidence
levels (0-5) and scores (0-100) using the rubric of Project Section 13:

    0 = Not mentioned             -> 0
    1 = Basic exposure            -> 20
    2 = Used in project           -> 40
    3 = Multiple projects/Intern  -> 60
    4 = Strong project + intern + cert -> 80
    5 = Advanced / strong evidence -> 100

Evidence level is derived transparently from a point system:
    +1  skill listed in Technical_Skills
    +1  per project referencing the skill (max 2)
    +1  internship referencing the skill
    +1  certification referencing the skill
    level = min(points, 5)
"""
import numpy as np
import pandas as pd

from .config import LEVEL_TO_SCORE, MASTER_SKILLS
from .skill_normalizer import build_evidence_frame


def evidence_level(mentions, project_hits, intern_hits, cert_hits):
    """Compute evidence level 0-5 from evidence counts."""
    points = 0
    if mentions:
        points += 1
    points += min(project_hits, 2)
    if intern_hits >= 1:
        points += 1
    if cert_hits >= 1:
        points += 1
    return min(points, 5)


def build_score_matrix(students_df):
    """Return a wide DataFrame: Roll_No, Student_Name, CGPI, <skill columns>."""
    evidence = build_evidence_frame(students_df)

    rows = []
    for _, erow in evidence.iterrows():
        record = {
            "Roll_No": erow["Roll_No"],
            "Student_Name": erow["Student_Name"],
        }
        for skill in MASTER_SKILLS:
            level = evidence_level(
                erow[f"{skill}::mentions"],
                erow[f"{skill}::project_hits"],
                erow[f"{skill}::intern_hits"],
                erow[f"{skill}::cert_hits"],
            )
            record[skill] = LEVEL_TO_SCORE[level]
        rows.append(record)

    matrix = pd.DataFrame(rows)
    matrix = matrix.merge(students_df[["Roll_No", "CGPI"]], on="Roll_No", how="left")
    return matrix
