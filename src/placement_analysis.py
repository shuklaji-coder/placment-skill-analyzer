"""Placement data analysis.

Answers questions Q1-Q4:
  Q1: Which companies recruited students in the previous three years?
  Q2: What were the most common job roles?
  Q3: What skills are most associated with these roles?
  Q4: How has the skill requirement changed over the three years?

Raw positions are normalised into role families so the distribution can be
interpreted.  Skill demand is derived from the role -> skill mapping weighted
by how often each role family appears in the placement records.
"""
import numpy as np
import pandas as pd

from .data_loader import load_role_skill_map

# Raw position -> role family (normalisation)
ROLE_FAMILY_MAP = [
    (("analyst /", "analyst"), "Analyst"),
    (("finance analyst",), "Analyst"),
    (("software engineer",), "Software Engineer / Developer"),
    (("systems engineer",), "Software Engineer / Developer"),
    (("system engineer",), "Software Engineer / Developer"),
    (("assistant system engineer",), "Software Engineer / Developer"),
    (("associate software engineer",), "Software Engineer / Developer"),
    (("programmer analyst",), "Software Engineer / Developer"),
    (("application development associate",), "Software Engineer / Developer"),
    (("packaged app development associate",), "Software Engineer / Developer"),
    (("project engineer",), "Software Engineer / Developer"),
    (("graduate engineer trainee",), "Software Engineer / Developer"),
    (("engineer trainee",), "Software Engineer / Developer"),
    (("executive engineer",), "Software Engineer / Developer"),
    (("implementation engineer",), "Software Engineer / Developer"),
    (("trainee developer",), "Software Engineer / Developer"),
    (("integration engineer",), "Software Engineer / Developer"),
    (("software analyst",), "Software Engineer / Developer"),
    (("graduate technical assistant",), "Software Engineer / Developer"),
    (("quant developer",), "Software Engineer / Developer"),
    (("associate ai/ml engineer",), "Software Engineer / Developer"),
    (("ai/ml engineer",), "Software Engineer / Developer"),
    (("jr embedded engineer",), "IoT / Embedded Engineer"),
    (("iot engineer",), "IoT / Embedded Engineer"),
    (("web designer",), "Web / Design"),
    (("seo -",), "Web / Design"),
    (("branch lead",), "Sales / Marketing / Operations"),
    (("advisor",), "Technical Support"),
    (("technical support",), "Technical Support"),
    (("operation assistant",), "Sales / Marketing / Operations"),
    (("technical sales",), "Sales / Marketing / Operations"),
    (("intern",), "Internship"),
]


def normalize_role(position):
    """Map a raw position string to a role family."""
    pos = position.lower()
    for keywords, family in ROLE_FAMILY_MAP:
        if all(kw in pos for kw in keywords):
            return family
    return "Other"


def add_role_family(placements):
    df = placements.copy()
    df["Role_Family"] = df["Position"].apply(normalize_role)
    return df


def placement_trend(placements):
    """Number of placements per year."""
    return placements.groupby("Year").size().rename("Count").reset_index()


def salary_by_year(placements):
    """Average and highest salary per year (NA rows excluded)."""
    num = placements.dropna(subset=["Salary_LPA"])
    if num.empty:
        return pd.DataFrame(columns=["Year", "Avg_Salary_LPA", "Max_Salary_LPA"])
    agg = (
        num.groupby("Year")["Salary_LPA"]
        .agg(["mean", "max"])
        .rename(columns={"mean": "Avg_Salary_LPA", "max": "Max_Salary_LPA"})
        .reset_index()
    )
    return agg


def top_recruiters(placements, n=10):
    """Most frequent recruiters across all three years."""
    counts = placements["Employer"].value_counts().reset_index()
    counts.columns = ["Employer", "Hires"]
    return counts.head(n)


def role_distribution(placements):
    """Placements grouped by role family."""
    df = add_role_family(placements)
    return df.groupby(["Role_Family", "Year"]).size().rename("Count").reset_index()


def skill_demand(placements):
    """Skill demand derived from the role -> skill mapping weighted by the
    frequency of each role family in the placement records."""
    placements = add_role_family(placements)
    role_map = load_role_skill_map()

    # Frequency of each role family (count of placements in that family)
    family_counts = placements["Role_Family"].value_counts()

    demand = {}
    for _, row in role_map.iterrows():
        role = row["Role"]
        family = normalize_role(role)  # role names align with role families
        weight = int(family_counts.get(family, 0))
        if weight == 0:
            continue
        for skill in row["Skills_List"]:
            demand[skill] = demand.get(skill, 0) + weight

    df = pd.DataFrame({"Skill": list(demand.keys()), "Demand_Weight": list(demand.values())})
    return df.sort_values("Demand_Weight", ascending=False).reset_index(drop=True)


def placement_analysis_summary(placements):
    """Combine the placement facts into a single summary table (export)."""
    trend = placement_trend(placements)
    salary = salary_by_year(placements)
    rec = top_recruiters(placements, n=None)
    roles = role_distribution(placements)
    return {
        "trend": trend,
        "salary": salary,
        "recruiters": rec,
        "roles": roles,
        "skill_demand": skill_demand(placements),
    }
