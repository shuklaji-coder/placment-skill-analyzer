"""Historical skill benchmark.

For every master skill the benchmark equals the mean of the historical
average scores across 2024, 2025 and 2026:

    Historical Benchmark = (2024 Score + 2025 Score + 2026 Score) / 3

The benchmark is computed dynamically from data/historical_skills.csv; it is
never hard-coded.  Master skills without a historical score receive NaN.
"""
import pandas as pd

from .config import HISTORICAL_GROUP_MAP, MASTER_SKILLS


def historical_skill_series(historical_df):
    """Pivot historical scores into {skill: {year: score}}."""
    series = {}
    for _, row in historical_df.iterrows():
        series.setdefault(row["Skill"], {})[int(row["Year"])] = float(row["Average_Score"])
    return series


def compute_benchmarks(historical_df):
    """Return DataFrame[Skill, 2024, 2025, 2026, Benchmark].

    Master skills inherit the benchmark of their historical skill group.
    """
    series = historical_skill_series(historical_df)
    # group averages per historical skill name
    group_avg = {}
    for name, years in series.items():
        values = [v for v in years.values() if not pd.isna(v)]
        group_avg[name] = sum(values) / len(values) if values else float("nan")

    rows = []
    for skill in MASTER_SKILLS:
        inherited = None
        for hist_name, master_list in HISTORICAL_GROUP_MAP.items():
            if skill in master_list:
                inherited = hist_name
                break
        row = {"Skill": skill}
        if inherited and inherited in series:
            years = series[inherited]
            row["2024"] = years.get(2024)
            row["2025"] = years.get(2025)
            row["2026"] = years.get(2026)
            row["Benchmark"] = group_avg[inherited]
            row["Historical_Group"] = inherited
        else:
            row["2024"] = row["2025"] = row["2026"] = row["Benchmark"] = None
            row["Historical_Group"] = "No Historical Data"
        rows.append(row)

    df = pd.DataFrame(rows)
    df["Benchmark"] = pd.to_numeric(df["Benchmark"], errors="coerce")
    return df


def benchmark_series_for_student(benchmark_df):
    """Return dict {skill: benchmark} (NaN when no historical group exists)."""
    return dict(zip(benchmark_df["Skill"], benchmark_df["Benchmark"]))
