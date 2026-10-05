"""Student -> job-role matching (Project Section 22).

For every student and every role:

    Role Match Score =
        Sum of student's scores in role-required skills
        --------------------------------------------------- x 100
        Maximum possible role score (100 x number of skills)

The top-3 roles are the roles with the highest match score.  For each role
the "missing skills" are the required skills where the student's score is
below the level expected for placement readiness (score < 60 by default, or
any required skill where a gap against the historical benchmark exists).
"""
import pandas as pd

from .config import MASTER_SKILLS
from .skill_gap import build_gap_long


def build_role_matches(score_matrix, role_map, benchmark_series):
    """Return a wide table: Roll_No, Role, Match_Score, Missing_Skills."""
    rows = []
    for _, srow in score_matrix.iterrows():
        for _, rrow in role_map.iterrows():
            role = rrow["Role"]
            required = rrow["Skills_List"]
            total = 0.0
            missing = []
            for skill in required:
                score = srow.get(skill, 0) or 0
                total += float(score)
                benchmark = benchmark_series.get(skill)
                if pd.isna(benchmark) or score < benchmark:
                    missing.append(skill)
            max_possible = 100.0 * len(required)
            match = round(total / max_possible * 100.0, 2) if max_possible else 0.0
            rows.append({
                "Roll_No": srow["Roll_No"],
                "Student_Name": srow["Student_Name"],
                "Role": role,
                "Match_Score": match,
                "Missing_Skills": "; ".join(missing),
            })
    return pd.DataFrame(rows)


def top_roles_for_student(role_matches, roll_no, top_n=3):
    """Top-n roles (by match score) for one student."""
    sub = role_matches[role_matches["Roll_No"] == roll_no]
    return sub.sort_values("Match_Score", ascending=False).head(top_n).reset_index(drop=True)


def best_role_for_student(role_matches, roll_no):
    """Single best (most suitable) role for one student."""
    top = top_roles_for_student(role_matches, roll_no, top_n=1)
    if top.empty:
        return None
    return top.iloc[0].to_dict()
