"""Data loading utilities.

Loads the raw source CSVs and applies light cleaning so every downstream
module consumes consistent data frames.
"""
import pandas as pd

from .config import (
    PLACEMENT_FILES,
    STUDENTS_FILE,
    HISTORICAL_SKILLS_FILE,
    ROLE_SKILL_MAP_FILE,
)


def load_placement_data():
    """Load all three years of placement records into a single DataFrame."""
    frames = []
    for year, path in sorted(PLACEMENT_FILES.items()):
        df = pd.read_csv(path, dtype={"Roll_No": str})
        df["Year"] = df["Year"].astype(int)
        frames.append(df)
    placements = pd.concat(frames, ignore_index=True)

    # Salary: keep "NA" records as NaN (analytically excluded from salary stats)
    placements["Salary_LPA"] = pd.to_numeric(placements["Salary_LPA"], errors="coerce")
    placements["Employer"] = placements["Employer"].astype(str).str.strip()
    placements["Position"] = placements["Position"].astype(str).str.strip()
    return placements


def load_students():
    """Load the 2027 student profiles (primary source: college profile PDF)."""
    df = pd.read_csv(STUDENTS_FILE, dtype={"Roll_No": str})
    df["Student_Name"] = df["Student_Name"].astype(str).str.strip()
    df["CGPI"] = pd.to_numeric(df["CGPI"], errors="coerce")
    for col in ["Technical_Skills", "Projects", "Internships", "Certifications", "GitHub"]:
        df[col] = df[col].fillna("NA").astype(str).str.strip()
    return df


def load_historical_skills():
    """Load the historical (2024-2026) average skill scores."""
    df = pd.read_csv(HISTORICAL_SKILLS_FILE)
    df["Year"] = df["Year"].astype(int)
    df["Skill"] = df["Skill"].astype(str).str.strip()
    df["Average_Score"] = pd.to_numeric(df["Average_Score"], errors="coerce")
    return df


def load_role_skill_map():
    """Load the job-role -> required skills mapping (Project Section 12)."""
    df = pd.read_csv(ROLE_SKILL_MAP_FILE)
    df["Role"] = df["Role"].astype(str).str.strip()
    df["Required_Skills"] = df["Required_Skills"].astype(str).str.strip()
    df["Skills_List"] = df["Required_Skills"].apply(
        lambda s: [x.strip() for x in s.split(",") if x.strip()]
    )
    return df
