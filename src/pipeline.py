"""End-to-end pipeline.

Runs the full analysis, writes every dataset / export, generates the static
report charts and the academic Markdown report.  All results are computed
from the source datasets — nothing is hard-coded.
"""
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from . import placement_analysis as pa
from . import recommendations as rec
from . import report as report_mod
from . import role_matching as rm
from . import skill_benchmark as sb
from . import skill_gap as sg
from . import student_scoring as ss
from .config import (
    OUTPUT_FILES,
    REPORTS_DIR,
    SKILL_BENCHMARK_FILE,
    SKILL_GAP_ANALYSIS_FILE,
    MASTER_SKILLS,
)
from .data_loader import (
    load_historical_skills,
    load_placement_data,
    load_role_skill_map,
    load_students,
)


def build_student_report(student_summary, score_matrix, gap_long, role_matches,
                         recommendations, role_map, per_student_skills):
    """Aggregate the per-student individual report (Project Section 18)."""
    summary_idx = student_summary.set_index("Roll_No")
    score_idx = score_matrix.set_index("Roll_No")
    rows = []
    for roll in score_idx.index:
        st = summary_idx.loc[roll]
        scores = score_idx.loc[roll]
        # Strong / Moderate / Weak across ALL master skills with evidence
        strong = [s for s in MASTER_SKILLS if scores[s] >= 80]
        moderate = [s for s in MASTER_SKILLS if 50 <= scores[s] < 80]
        weak = [s for s in MASTER_SKILLS if 0 < scores[s] < 50]
        # Missing skills are restricted to the student's own relevant skill set
        # (skills required by their top matched roles) so irrelevant skills do
        # not clutter the report.
        missing = [s for s in per_student_skills.get(roll, []) if scores[s] == 0]

        sub_gap = gap_long[gap_long["Roll_No"] == roll].sort_values("Gap", ascending=False)
        top5 = sub_gap.head(5)
        top5_txt = "; ".join(
            f"{g['Skill']} ({g['Gap']:g})" for _, g in top5.iterrows()
        ) if not top5.empty else "No significant gaps"

        role_sub = role_matches[role_matches["Roll_No"] == roll]
        role_sub = role_sub.sort_values("Match_Score", ascending=False)
        suitable = role_sub[role_sub["Match_Score"] >= 60]["Role"].tolist()
        target = role_sub.head(3)["Role"].tolist()

        rec_sub = recommendations[recommendations["Roll_No"] == roll]
        if rec_sub.empty:
            plan_txt = "No critical/high/moderate gaps - maintain current level"
        else:
            plan_txt = " | ".join(
                f"{g['Skill']} ({g['Gap_Level']}): {g['Recommended_Topics']}"
                for _, g in rec_sub.iterrows()
            )

        rows.append({
            "Roll_No": roll,
            "Student_Name": st["Student_Name"],
            "CGPI": st["CGPI"],
            "Overall_Skill": st["Overall_Skill"],
            "Overall_Gap": st["Overall_Gap"],
            "Placement_Readiness": st["Placement_Readiness"],
            "Readiness_Level": st["Readiness_Level"],
            "Strong_Skills": "; ".join(strong) or "No strong skills recorded",
            "Moderate_Skills": "; ".join(moderate) or "No moderate skills recorded",
            "Weak_Skills": "; ".join(weak) or "No weak skills recorded",
            "Missing_Skills": "; ".join(missing) or "No missing skills",
            "Top_5_Gaps": top5_txt,
            "Current_Suitable_Roles": "; ".join(suitable) or "No role above 60% match yet",
            "Target_Roles": "; ".join(target) or "No roles matched",
            "Personalized_Training_Plan": plan_txt,
        })
    return pd.DataFrame(rows)


def _write_csv(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def generate_report_charts(analysis):
    """Save static matplotlib charts used inside the written report."""
    chart_dir = REPORTS_DIR / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)

    # 1. Placement trend + salary
    fig, ax = plt.subplots(figsize=(8, 4))
    trend = analysis["placement"]["trend"]
    ax.bar(trend["Year"].astype(str), trend["Count"], color="#4C72B0")
    ax.set_title("Placements per Year (2024-2026)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Placements")
    fig.tight_layout()
    fig.savefig(chart_dir / "placement_trend.png", dpi=120)
    plt.close(fig)

    # 2. Historical benchmark
    fig, ax = plt.subplots(figsize=(10, 4))
    bench = analysis["benchmark_df"].dropna(subset=["Benchmark"]).sort_values("Benchmark")
    ax.barh(bench["Skill"], bench["Benchmark"], color="#55A868")
    ax.set_title("Historical Skill Benchmark (2024-2026 mean)")
    ax.set_xlabel("Benchmark score")
    fig.tight_layout()
    fig.savefig(chart_dir / "historical_benchmark.png", dpi=120)
    plt.close(fig)

    # 3. 2027 average skill level vs benchmark
    fig, ax = plt.subplots(figsize=(12, 5))
    scores = analysis["score_matrix"][analysis["relevant_skills"]].mean().sort_values()
    names = scores.index.tolist()
    ax.barh(names, scores.values, color="#C44E52")
    ax.set_title("2027 Batch Average Skill Score")
    ax.set_xlabel("Average score")
    fig.tight_layout()
    fig.savefig(chart_dir / "student_avg_skills.png", dpi=120)
    plt.close(fig)

    # 4. Skill gap ranking (batch average gap)
    fig, ax = plt.subplots(figsize=(10, 5))
    avg_gap = analysis["gap_long"].groupby("Skill")["Gap"].mean().sort_values()
    ax.barh(avg_gap.index.tolist(), avg_gap.values, color="#EDB852")
    ax.set_title("Batch Average Skill Gap Ranking")
    ax.set_xlabel("Average gap")
    fig.tight_layout()
    fig.savefig(chart_dir / "skill_gap_ranking.png", dpi=120)
    plt.close(fig)

    # 5. Placement readiness distribution
    fig, ax = plt.subplots(figsize=(8, 4))
    counts = analysis["student_summary"]["Readiness_Level"].value_counts()
    ax.bar(counts.index, counts.values, color="#8C8C8C")
    ax.set_title("Placement Readiness Distribution (2027 batch)")
    ax.set_ylabel("Students")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(chart_dir / "readiness_distribution.png", dpi=120)
    plt.close(fig)


def run_pipeline(write_outputs=True):
    """Execute the full analysis and return a dict with all artefacts."""
    students = load_students()
    placements = load_placement_data()
    historical = load_historical_skills()
    role_map = load_role_skill_map()

    # Placement analysis (Q1-Q4)
    placement = pa.placement_analysis_summary(placements)

    # Historical benchmark (dynamic)
    benchmark_df = sb.compute_benchmarks(historical)
    benchmark_series = dict(zip(benchmark_df["Skill"], benchmark_df["Benchmark"]))

    # Student skill scoring (evidence-based)
    score_matrix = ss.build_score_matrix(students)
    relevant = sg.relevant_skills(role_map)

    # Gap analysis
    gap_matrix, skills_used = sg.build_gap_matrix(score_matrix, benchmark_series, role_map)

    # Role matching first (the per-student relevant skill set depends on it)
    role_matches = rm.build_role_matches(score_matrix, role_map, benchmark_series)
    per_student_skills = sg.per_student_relevant_skills(role_matches, role_map)

    student_summary = sg.build_student_summary(
        score_matrix, benchmark_series, role_map, role_matches
    )
    gap_long = sg.build_gap_long(score_matrix, benchmark_series, role_map)

    # Recommendations
    recommendations = rec.build_recommendations(gap_long, role_matches, per_student_skills)
    student_report = build_student_report(
        student_summary, score_matrix, gap_long, role_matches,
        recommendations, role_map, per_student_skills,
    )

    analysis = {
        "students": students,
        "placements": placements,
        "placement": placement,
        "historical": historical,
        "benchmark_df": benchmark_df,
        "benchmark_series": benchmark_series,
        "score_matrix": score_matrix,
        "gap_matrix": gap_matrix,
        "relevant_skills": relevant,
        "student_summary": student_summary,
        "gap_long": gap_long,
        "role_matches": role_matches,
        "recommendations": recommendations,
        "student_report": student_report,
        "role_map": role_map,
        "per_student_skills": per_student_skills,
    }

    if write_outputs:
        _write_outputs(analysis)
    return analysis


def _write_outputs(analysis):
    """Persist all datasets, exports and the report."""
    # data/ calculated files
    _write_csv(analysis["benchmark_df"], SKILL_BENCHMARK_FILE)
    _write_csv(analysis["gap_long"], SKILL_GAP_ANALYSIS_FILE)

    # outputs/
    _write_csv(analysis["score_matrix"], OUTPUT_FILES["student_scores"])
    _write_csv(analysis["gap_long"], OUTPUT_FILES["skill_gap"])
    _write_csv(analysis["student_report"], OUTPUT_FILES["report"])
    _write_csv(analysis["role_matches"], OUTPUT_FILES["role_match"])
    _write_csv(analysis["recommendations"], OUTPUT_FILES["recommendations"])
    _write_csv(analysis["benchmark_df"], OUTPUT_FILES["benchmark"])

    # Placement analysis export: recruiter hires split by year (answers Q1)
    placements = analysis["placements"]
    recruit_pivot = placements.groupby(["Employer", "Year"]).size().unstack(fill_value=0).reset_index()
    recruit_pivot.columns = [str(c) for c in recruit_pivot.columns]
    year_cols = [c for c in recruit_pivot.columns if c != "Employer"]
    recruit_pivot["Total_Hires"] = recruit_pivot[year_cols].sum(axis=1)
    recruit_pivot = recruit_pivot.sort_values("Total_Hires", ascending=False).reset_index(drop=True)
    _write_csv(recruit_pivot, OUTPUT_FILES["placement"])

    # placement analysis export (flattened)
    p = analysis["placement"]
    with pd.ExcelWriter(OUTPUT_FILES["excel"], engine="openpyxl") as writer:
        analysis["placements"].to_excel(writer, sheet_name="Placement_Data", index=False)
        p["trend"].to_excel(writer, sheet_name="Placement_Trend", index=False)
        p["salary"].to_excel(writer, sheet_name="Salary_By_Year", index=False)
        p["recruiters"].to_excel(writer, sheet_name="Top_Recruiters", index=False)
        p["roles"].to_excel(writer, sheet_name="Role_Distribution", index=False)
        p["skill_demand"].to_excel(writer, sheet_name="Skill_Demand", index=False)
        analysis["historical"].to_excel(writer, sheet_name="Historical_Skills", index=False)
        analysis["benchmark_df"].to_excel(writer, sheet_name="Skill_Benchmark", index=False)
        analysis["score_matrix"].to_excel(writer, sheet_name="Student_Skill_Matrix", index=False)
        analysis["gap_long"].to_excel(writer, sheet_name="Skill_Gap_Analysis", index=False)
        analysis["student_summary"].to_excel(writer, sheet_name="Student_Summary", index=False)
        analysis["role_matches"].to_excel(writer, sheet_name="Role_Matches", index=False)
        analysis["recommendations"].to_excel(writer, sheet_name="Recommendations", index=False)
        analysis["student_report"].to_excel(writer, sheet_name="Student_Reports", index=False)

    generate_report_charts(analysis)
    report_mod.write_final_report(analysis)
    return analysis


def print_summary(analysis):
    summary = analysis["student_summary"]
    print(f"Students analysed       : {summary.shape[0]}")
    print(f"Average CGPI            : {summary['CGPI'].mean():.2f}")
    print(f"Average Overall Skill   : {summary['Overall_Skill'].mean():.2f}")
    print(f"Average Overall Gap     : {summary['Overall_Gap'].mean():.2f}")
    print(f"Average Readiness       : {summary['Placement_Readiness'].mean():.2f}")
    print(f"Critical-gap students   : {(summary['Num_Critical_Gaps'] > 0).sum()}")
    print("\nPlacement readiness distribution:")
    print(summary["Readiness_Level"].value_counts().to_string())
    print("\nTop 5 overall gaps by skill (batch average):")
    ag = analysis["gap_long"].groupby("Skill")["Gap"].mean().sort_values(ascending=False).head(5)
    print(ag.round(2).to_string())


if __name__ == "__main__":
    analysis = run_pipeline(write_outputs=True)
    print_summary(analysis)
    print("\nOutputs written to outputs/, data/, reports/")
