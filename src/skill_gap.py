"""Skill gap calculation.

For every student and every relevant placement skill:

    Skill Gap = Historical Benchmark - Student Skill Score      (min 0)

Gap levels (Project Section 15):
    0-5   -> Very Low / No Gap
    5-10  -> Low Gap
    10-20 -> Moderate Gap
    20-30 -> High Gap
    30+   -> Critical Gap

Overall gap (Project Section 16) is the mean of the individual gaps over all
*relevant placement skills* only (the union of skills required by the target
job roles), so irrelevant skills do not penalise a student.

Placement readiness (Project Section 17):
    Placement Readiness = 100 - Overall Skill Gap
"""
import numpy as np
import pandas as pd

from .config import classify_gap, classify_readiness


def relevant_skills(role_map):
    """Union of all skills required across the job-role catalogue."""
    skills = set()
    for _, row in role_map.iterrows():
        skills.update(row["Skills_List"])
    return sorted(skills)


def per_student_relevant_skills(role_matches, role_map, top_roles=3):
    """Dict {roll_no: [skills required by the student's top-N matched roles]}."""
    role_skill = dict(zip(role_map["Role"], role_map["Skills_List"]))
    result = {}
    for roll in role_matches["Roll_No"].unique():
        top = role_matches[role_matches["Roll_No"] == roll]
        top = top.sort_values("Match_Score", ascending=False).head(top_roles)
        skills = set()
        for _, r in top.iterrows():
            skills.update(role_skill.get(r["Role"], []))
        result[roll] = sorted(skills)
    return result


def build_gap_matrix(score_matrix, benchmark_series, role_map):
    """Wide matrix of gaps: rows = students, cols = relevant skills."""
    skills = relevant_skills(role_map)

    gap_rows = []
    for _, srow in score_matrix.iterrows():
        record = {"Roll_No": srow["Roll_No"], "Student_Name": srow["Student_Name"], "CGPI": srow["CGPI"]}
        for skill in skills:
            benchmark = benchmark_series.get(skill, np.nan)
            student = srow.get(skill, 0)
            if pd.isna(benchmark) or pd.isna(student):
                record[skill] = np.nan
            else:
                record[skill] = max(0.0, round(float(benchmark) - float(student), 2))
        gap_rows.append(record)
    return pd.DataFrame(gap_rows), skills


def build_student_summary(score_matrix, benchmark_series, role_map, role_matches,
                          top_roles=3):
    """Per-student overall scores: Overall_Skill, Overall_Gap, Placement_Readiness.

    Per Project Section 16, only skills relevant to the student's own placement
    target count.  The relevant skill set is the union of the skills required by
    the student's top-N matched job roles, so a student targeting Software
    Engineering is not penalised for missing e.g. PCB design.
    """
    per_student_skills = per_student_relevant_skills(role_matches, role_map, top_roles)

    rows = []
    for _, srow in score_matrix.iterrows():
        skills = per_student_skills[srow["Roll_No"]]
        scores = []
        gaps = []
        for skill in skills:
            benchmark = benchmark_series.get(skill, np.nan)
            student = srow.get(skill, 0)
            if pd.isna(benchmark):
                continue  # no historical benchmark -> not part of gap denominator
            if pd.isna(student):
                student = 0.0
            scores.append(float(student))
            gaps.append(max(0.0, float(benchmark) - float(student)))

        overall_skill = round(float(np.mean(scores)), 2) if scores else 0.0
        overall_gap = round(float(np.mean(gaps)), 2) if gaps else 0.0
        readiness = round(100.0 - overall_gap, 2)

        rows.append({
            "Roll_No": srow["Roll_No"],
            "Student_Name": srow["Student_Name"],
            "CGPI": srow["CGPI"],
            "Overall_Skill": overall_skill,
            "Overall_Gap": overall_gap,
            "Placement_Readiness": readiness,
            "Readiness_Level": classify_readiness(readiness),
            "Relevant_Skills": "; ".join(skills),
            "Num_Critical_Gaps": 0,  # filled below
            "Num_High_Gaps": 0,
            "Num_Moderate_Gaps": 0,
        })
    summary = pd.DataFrame(rows)

    # Gap counts are computed only over each student's own relevant skills.
    count_rows = []
    for _, srow in score_matrix.iterrows():
        skills = per_student_skills[srow["Roll_No"]]
        n_crit = n_high = n_mod = 0
        for skill in skills:
            benchmark = benchmark_series.get(skill, np.nan)
            student = srow.get(skill, 0)
            if pd.isna(benchmark) or pd.isna(student):
                continue
            gap = max(0.0, float(benchmark) - float(student))
            level = classify_gap(gap)
            if level == "Critical Gap":
                n_crit += 1
            elif level == "High Gap":
                n_high += 1
            elif level == "Moderate Gap":
                n_mod += 1
        count_rows.append({
            "Roll_No": srow["Roll_No"],
            "Num_Critical_Gaps": n_crit,
            "Num_High_Gaps": n_high,
            "Num_Moderate_Gaps": n_mod,
        })
    counts = pd.DataFrame(count_rows)
    summary = summary.drop(columns=["Num_Critical_Gaps", "Num_High_Gaps", "Num_Moderate_Gaps"])
    summary = summary.merge(counts, on="Roll_No")
    return summary


def build_gap_long(score_matrix, benchmark_series, role_map, summary=None):
    """Long-format gap table: one row per student-skill (Project Section 21)."""
    skills = relevant_skills(role_map)
    rows = []
    for _, srow in score_matrix.iterrows():
        for skill in skills:
            benchmark = benchmark_series.get(skill, np.nan)
            student = srow.get(skill, 0)
            if pd.isna(benchmark) or pd.isna(student):
                continue
            gap = round(max(0.0, float(benchmark) - float(student)), 2)
            rows.append({
                "Roll_No": srow["Roll_No"],
                "Student_Name": srow["Student_Name"],
                "Skill": skill,
                "Student_Score": float(student),
                "Historical_Benchmark": round(float(benchmark), 2),
                "Gap": gap,
                "Gap_Level": classify_gap(gap),
            })
    return pd.DataFrame(rows)
