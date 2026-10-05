"""Interactive Streamlit dashboard.

Placement-Based Individual Skill Gap Analysis of 2027 IoT Batch Students.

Run from the project root:
    streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import MASTER_SKILLS, SYNTHETIC_2026_NOTE  # noqa: E402
from src import report as report_mod  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402

st.set_page_config(
    page_title="Placement Skill Gap Analysis - 2027 IoT Batch",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme / palette
# ---------------------------------------------------------------------------
COLORS = {
    "primary": "#4C72B0",
    "green": "#55A868",
    "red": "#C44E52",
    "gold": "#EDB852",
    "navy": "#26456e",
    "grey": "#8C8C8C",
}

# ---------------------------------------------------------------------------
# Data (cached)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Computing the full analysis pipeline ...")
def get_analysis():
    return run_pipeline(write_outputs=True)


ANALYSIS = get_analysis()


def students_filtered(filters, summary_df):
    """Return roll numbers after applying student-level filters."""
    rolls = set(summary_df["Roll_No"])
    if filters.get("students"):
        rolls &= set(filters["students"])
    if filters.get("cgpi"):
        lo, hi = filters["cgpi"]
        sub = summary_df[(summary_df["CGPI"] >= lo) & (summary_df["CGPI"] <= hi)]
        rolls &= set(sub["Roll_No"])
    if filters.get("gap_levels"):
        sub = summary_df[
            summary_df["Readiness_Level"].isin(filters["gap_levels"])
            | summary_df["Readiness_Level"].eq("High Training Requirement")
        ]
        rolls &= set(sub["Roll_No"])
    return sorted(rolls)


# ---------------------------------------------------------------------------
# Sidebar: navigation + filters
# ---------------------------------------------------------------------------
PAGES = [
    "📊 Overview Dashboard",
    "🧠 Skill Gap Analysis",
    "🔥 Student x Skill Gap Heatmap",
    "👤 Student Profiles",
    "💼 Job Role Matching",
    "❓ Project Questions (Q1-Q10)",
    "🎓 Academic Conclusion",
    "📥 Exports & Datasets",
    "ℹ️ About & Methodology",
]

with st.sidebar:
    st.title("Skill Gap Analyzer")
    st.caption("2027 IoT Batch | Placement-Based Analysis")
    page = st.radio("Navigation", PAGES, label_visibility="collapsed")

    st.divider()
    with st.expander("🎚️ Filters", expanded=True):
        student_names = ANALYSIS["students"]["Student_Name"].tolist()
        sel_students = st.multiselect(
            "Student", student_names, placeholder="All students"
        )
        cgpi = st.slider("CGPI range", 0.0, 10.0, (0.0, 10.0), 0.1)
        years = st.multiselect("Year", [2024, 2025, 2026], default=[2024, 2025, 2026])
        skills_opts = ANALYSIS["relevant_skills"]
        sel_skills = st.multiselect("Skill", skills_opts, placeholder="All skills")
        sel_roles = st.multiselect(
            "Job Role", ANALYSIS["role_map"]["Role"].tolist(), placeholder="All roles"
        )
        sel_gaps = st.multiselect(
            "Readiness level",
            ["Highly Placement Ready", "Placement Ready", "Needs Improvement",
             "High Training Requirement"],
            placeholder="All levels",
        )
        companies = sorted(ANALYSIS["placements"]["Employer"].unique().tolist())
        sel_companies = st.multiselect("Company", companies, placeholder="All companies")

    st.divider()

filters = {
    "students": sel_students,
    "cgpi": cgpi,
    "years": years,
    "skills": sel_skills,
    "roles": sel_roles,
    "gap_levels": sel_gaps,
    "companies": sel_companies,
}

summary = ANALYSIS["student_summary"]
rolls = students_filtered(filters, summary)

# ===========================================================================
# PAGE 1 - OVERVIEW DASHBOARD
# ===========================================================================
def page_overview():
    st.header("Overview Dashboard")
    st.markdown(
        "Placement-Based Individual Skill Gap Analysis of the 2027 IoT Batch, built "
        "from the previous three years (2024-2026) of placement records."
    )

    k = ANALYSIS
    sub = summary[summary["Roll_No"].isin(rolls)]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Students", f"{len(sub)}")
    c2.metric("Average CGPI", f"{sub['CGPI'].mean():.2f}")
    c3.metric("Avg Skill Score", f"{sub['Overall_Skill'].mean():.1f}")
    c4.metric("Avg Skill Gap", f"{sub['Overall_Gap'].mean():.1f}")
    c5.metric("Avg Placement Readiness", f"{sub['Placement_Readiness'].mean():.1f}")
    c6.metric("Students w/ Critical Gaps", f"{int((sub['Num_Critical_Gaps'] > 0).sum())}")

    st.divider()
    st.subheader("1. Historical Placement Trend")
    col_a, col_b = st.columns(2)

    # Chart 1: placements per year
    trend = k["placement"]["trend"]
    trend = trend[trend["Year"].isin(filters["years"])]
    fig = px.bar(trend, x="Year", y="Count", color_discrete_sequence=[COLORS["primary"]],
                 labels={"Count": "Placements"}, title="Placements per Year")
    col_a.plotly_chart(fig, width="stretch")

    # Chart 2 & 3: average / highest salary by year
    salary = k["placement"]["salary"]
    salary = salary[salary["Year"].isin(filters["years"])]
    fig2 = px.bar(salary, x="Year", y="Avg_Salary_LPA",
                  color_discrete_sequence=[COLORS["green"]],
                  labels={"Avg_Salary_LPA": "LPA"},
                  title="Average Salary by Year (LPA)")
    col_b.plotly_chart(fig2, width="stretch")

    col_c, col_d = st.columns(2)
    fig3 = px.bar(salary, x="Year", y="Max_Salary_LPA",
                  color_discrete_sequence=[COLORS["red"]],
                  labels={"Max_Salary_LPA": "LPA"},
                  title="Highest Salary by Year (LPA)")
    col_c.plotly_chart(fig3, width="stretch")

    # Chart 4: top recruiters
    rec = k["placement"]["recruiters"]
    if filters["companies"]:
        rec = rec[rec["Employer"].isin(filters["companies"])]
    fig4 = px.bar(rec.sort_values("Hires"), x="Hires", y="Employer", orientation="h",
                  color_discrete_sequence=[COLORS["navy"]],
                  title="Top Recruiters (2024-2026)", labels={"Hires": "Hires"})
    fig4.update_layout(height=520)
    col_d.plotly_chart(fig4, width="stretch")

    st.divider()
    st.subheader("2. Job Roles & Skill Demand")

    col_e, col_f = st.columns(2)
    # Chart 5: role distribution
    roles = k["placement"]["roles"]
    roles = roles[roles["Year"].isin(filters["years"])]
    role_agg = roles.groupby("Role_Family")["Count"].sum().sort_values()
    fig5 = px.bar(role_agg, x="Count", y=role_agg.index, orientation="h",
                  color_discrete_sequence=[COLORS["gold"]],
                  title="Job Role Distribution (Normalised)")
    col_e.plotly_chart(fig5, width="stretch")

    # Chart 6: most required skills (weighted demand)
    demand = k["placement"]["skill_demand"]
    if filters["skills"]:
        demand = demand[demand["Skill"].isin(filters["skills"])]
    fig6 = px.bar(demand.head(15).sort_values("Demand_Weight"),
                  x="Demand_Weight", y="Skill", orientation="h",
                  color_discrete_sequence=[COLORS["primary"]],
                  title="Most Required Skills (role demand weighted by hires)")
    col_f.plotly_chart(fig6, width="stretch")

    st.divider()
    st.subheader("3. Historical Benchmark vs 2027 Batch")

    col_g, col_h = st.columns(2)
    # Chart 7: historical skill benchmark by year
    hist = k["historical"]
    hist = hist[hist["Year"].isin(filters["years"])]
    fig7 = px.line(hist, x="Skill", y="Average_Score", color="Year",
                   markers=True, title="Historical Skill Scores by Year",
                   color_discrete_sequence=[COLORS["primary"], COLORS["green"], COLORS["gold"]])
    col_g.plotly_chart(fig7, width="stretch")

    # Chart 8: 2027 average skill level vs benchmark
    bench = k["benchmark_df"].dropna(subset=["Benchmark"])
    if filters["skills"]:
        bench = bench[bench["Skill"].isin(filters["skills"])]
    avg_2027 = k["score_matrix"][bench["Skill"].tolist()].mean().rename("Student_Avg")
    cmp_df = bench.set_index("Skill")[["Benchmark"]].join(avg_2027).reset_index()
    fig8 = go.Figure()
    fig8.add_bar(x=cmp_df["Skill"], y=cmp_df["Benchmark"], name="Historical Benchmark",
                 marker_color=COLORS["grey"])
    fig8.add_bar(x=cmp_df["Skill"], y=cmp_df["Student_Avg"], name="2027 Batch Average",
                 marker_color=COLORS["green"])
    fig8.update_layout(title="2027 Average Skill Level vs Historical Benchmark",
                       barmode="group", xaxis_tickangle=-45)
    col_h.plotly_chart(fig8, width="stretch")


# ===========================================================================
# PAGE 2 - SKILL GAP ANALYSIS
# ===========================================================================
def page_gap_analysis():
    st.header("Skill Gap Analysis")
    k = ANALYSIS
    gap_long = k["gap_long"]
    sub_summary = summary[summary["Roll_No"].isin(rolls)]
    gap_long = gap_long[gap_long["Roll_No"].isin(rolls)]
    if filters["skills"]:
        gap_long = gap_long[gap_long["Skill"].isin(filters["skills"])]

    st.subheader("9. Skill Gap Ranking (batch average gap)")
    avg_gap = gap_long.groupby("Skill")["Gap"].mean().sort_values()
    fig = px.bar(avg_gap, x="Gap", y=avg_gap.index, orientation="h",
                 color=avg_gap.values, color_continuous_scale="RdYlGn_r",
                 title="Average Skill Gap per Skill (2027 batch)")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch")

    st.subheader("10. Critical & High Skill Gaps (students affected)")
    crit = gap_long[gap_long["Gap_Level"].isin(["Critical Gap", "High Gap"])]
    crit_counts = crit.groupby("Skill")["Roll_No"].nunique().sort_values()
    if not crit_counts.empty:
        fig = px.bar(crit_counts, x="Roll_No", y=crit_counts.index, orientation="h",
                     color_discrete_sequence=[COLORS["red"]],
                     title="Number of Students with Critical/High Gap per Skill",
                     labels={"Roll_No": "Students"})
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No critical/high gaps with the current filters.")

    st.subheader("11. Student Placement Readiness")
    col_a, col_b = st.columns([3, 2])
    read = sub_summary.sort_values("Placement_Readiness")
    fig = px.bar(read, x="Student_Name", y="Placement_Readiness",
                 color="Readiness_Level",
                 color_discrete_map={
                     "Highly Placement Ready": COLORS["green"],
                     "Placement Ready": "#6BA86B",
                     "Needs Improvement": COLORS["gold"],
                     "High Training Requirement": COLORS["red"],
                 },
                 title="Placement Readiness by Student (100 - Overall Gap)")
    fig.update_layout(xaxis_tickangle=-60)
    col_a.plotly_chart(fig, width="stretch")

    fig2 = px.scatter(sub_summary, x="CGPI", y="Placement_Readiness",
                      color="Readiness_Level", hover_name="Student_Name",
                      title="Readiness vs CGPI",
                      color_discrete_map={
                          "Highly Placement Ready": COLORS["green"],
                          "Placement Ready": "#6BA86B",
                          "Needs Improvement": COLORS["gold"],
                          "High Training Requirement": COLORS["red"],
                      })
    col_b.plotly_chart(fig2, width="stretch")

    st.subheader("Gap Level Distribution (student-skill level)")
    dist = gap_long["Gap_Level"].value_counts().reindex(
        ["Critical Gap", "High Gap", "Moderate Gap", "Low Gap", "Very Low / No Gap"]
    ).fillna(0)
    fig = px.pie(values=dist.values, names=dist.index,
                 title="Distribution of Skill-Gap Levels",
                 color_discrete_sequence=[COLORS["red"], COLORS["gold"],
                                          "#e3a8a8", "#a8c3e3", COLORS["green"]])
    st.plotly_chart(fig, width="stretch")


# ===========================================================================
# PAGE 3 - HEATMAP
# ===========================================================================
def page_heatmap():
    st.header("Student x Skill Gap Heatmap")
    k = ANALYSIS
    gap_long = k["gap_long"]

    st.markdown(
        "Rows are students, columns are placement-relevant skills, cell values "
        "are the individual **skill gap** (`Historical Benchmark - Student Score`). "
        "Dark red = critical gap, green = no gap."
    )

    st.markdown("#### 12. Individual Skill Gap Heatmap")
    heat_skills = filters["skills"] or list(gap_long["Skill"].unique())
    heat_rolls = rolls
    sub = gap_long[(gap_long["Skill"].isin(heat_skills)) &
                   (gap_long["Roll_No"].isin(heat_rolls))]
    if sub.empty:
        st.warning("No data for the current filter selection.")
        return

    pivot = sub.pivot(index="Roll_No", columns="Skill", values="Gap")
    pivot = pivot.reindex(sorted(pivot.index, key=lambda r: (summary.set_index("Roll_No").loc[r, "Placement_Readiness"] if r in summary.set_index("Roll_No").index else 0)))
    z = pivot.values
    xlabels = pivot.columns.tolist()
    ylabels = pivot.index.tolist()

    names = k["students"].set_index("Roll_No")["Student_Name"].to_dict()
    hover = np.empty(z.shape, dtype=object)
    for i, r in enumerate(ylabels):
        for j, s in enumerate(xlabels):
            hover[i, j] = (f"{names.get(r, r)} | {s}<br>Gap: {z[i, j]:.1f}"
                           if not pd.isna(z[i, j]) else "No benchmark")

    fig = go.Figure(data=go.Heatmap(
        z=z, x=xlabels, y=ylabels,
        colorscale="RdYlGn_r",
        zmin=0, zmax=max(35.0, np.nanmax(z) if z.size else 35),
        text=hover, hoverinfo="text",
        colorbar={"title": "Gap"},
    ))
    fig.update_layout(height=max(520, 14 * len(ylabels) + 200),
                      xaxis_tickangle=-45, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### Skill matrix (student scores)")
    scores = k["score_matrix"].set_index("Roll_No")
    score_sub = scores.loc[[r for r in ylabels if r in scores.index],
                           [s for s in heat_skills if s in scores.columns]]
    score_sub.index = score_sub.index.map(lambda r: names.get(r, r))
    st.dataframe(score_sub.style.background_gradient(cmap="Greens", vmin=0, vmax=100),
                 width="stretch", height=420)


# ===========================================================================
# PAGE 4 - STUDENT PROFILES
# ===========================================================================
def page_profiles():
    st.header("Student Profile")
    k = ANALYSIS
    students = k["students"].set_index("Roll_No")
    per_student_skills = k["per_student_skills"]
    gap_long = k["gap_long"]
    score_matrix = k["score_matrix"].set_index("Roll_No")
    role_matches = k["role_matches"]
    recommendations = k["recommendations"]

    options = students["Student_Name"].tolist()
    name = st.selectbox("Select a student", options)

    st.divider()

    roll = students[students["Student_Name"] == name].index[0]
    row = students.loc[roll]
    summ = summary.set_index("Roll_No").loc[roll]
    scores = score_matrix.loc[roll][MASTER_SKILLS]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Name", name)
    c2.metric("Roll No", roll)
    c3.metric("CGPI", f"{row['CGPI']:.2f}")
    c4.metric("Placement Readiness", f"{summ['Placement_Readiness']:.1f} / 100",
              delta=f"{summ['Readiness_Level']}")

    git = row["GitHub"]
    if git and git not in ("NA", "None", "."):
        st.markdown(f"**GitHub:** [{git}]({git})")

    st.divider()

    # --- Skill radar (top skills with evidence) ---
    st.subheader("Skill Radar Chart")
    top_skills = scores[scores > 0].sort_values(ascending=False).head(10)
    radar_skills = top_skills.index.tolist() if len(top_skills) else []
    radar_vals = top_skills.values.tolist() if len(top_skills) else []
    if radar_skills:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=radar_vals + radar_vals[:1],
            theta=radar_skills + radar_skills[:1],
            fill="toself", name="Skill Score",
            line_color=COLORS["primary"],
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                          showlegend=False)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No technical skill evidence recorded for this student.")

    # --- Strong / Moderate / Weak / Missing ---
    strong = scores[scores >= 80].index.tolist()
    moderate = scores[(scores >= 50) & (scores < 80)].index.tolist()
    weak = scores[(scores > 0) & (scores < 50)].index.tolist()
    relevant = per_student_skills.get(roll, [])
    missing = [s for s in relevant if scores.get(s, 0) == 0]

    col_a, col_b = st.columns(2)
    col_a.markdown("**Strong Skills** (> 80)")
    col_a.write(", ".join(strong) if strong else "No strong skills recorded")
    col_a.markdown("**Moderate Skills** (50-79)")
    col_a.write(", ".join(moderate) if moderate else "No moderate skills recorded")
    col_b.markdown("**Weak Skills** (1-49)")
    col_b.write(", ".join(weak) if weak else "No weak skills recorded")
    col_b.markdown("**Missing Skills** (target-role skills at 0)")
    col_b.write(", ".join(missing) if missing else "No missing skills")

    # --- Top 5 gaps ---
    st.subheader("Top 5 Skill Gaps")
    sub_gap = gap_long[gap_long["Roll_No"] == roll].sort_values("Gap", ascending=False).head(5)
    if not sub_gap.empty:
        fig = px.bar(sub_gap, x="Skill", y="Gap", color="Gap_Level",
                     color_discrete_map={
                         "Critical Gap": COLORS["red"], "High Gap": COLORS["gold"],
                         "Moderate Gap": "#e3a8a8", "Low Gap": "#a8c3e3",
                         "Very Low / No Gap": COLORS["green"]},
                     title="Largest skill gaps for this student")
        fig.add_hline(y=0, line_dash="dash", line_color="grey")
        st.plotly_chart(fig, width="stretch")

    # --- Suitable roles ---
    st.subheader("Suitable Job Roles (role match score)")
    role_sub = role_matches[role_matches["Roll_No"] == roll].sort_values("Match_Score", ascending=False)
    for _, r in role_sub.head(3).iterrows():
        st.markdown(f"**{r['Role']}** — {r['Match_Score']:.1f}%")
        if r["Missing_Skills"]:
            st.caption("Needs for this role: " + r["Missing_Skills"])

    # --- Training plan ---
    st.subheader("Personalized Training Recommendations")
    plan = k["recommendations"]
    plan_sub = plan[plan["Roll_No"] == roll].sort_values("Gap", ascending=False)
    if plan_sub.empty:
        st.success("No critical/high/moderate gaps in target-role skills. Maintain current level.")
    for _, r in plan_sub.head(8).iterrows():
        with st.expander(f"{r['Skill']} — {r['Gap_Level']} (gap {r['Gap']:.1f})"):
            st.markdown("**Recommended topics:** " + r["Recommended_Topics"])


# ===========================================================================
# PAGE 5 - JOB ROLE MATCHING
# ===========================================================================
def page_roles():
    st.header("Student -> Job Role Matching")
    k = ANALYSIS
    role_matches = k["role_matches"]

    if filters["roles"]:
        role_matches = role_matches[role_matches["Role"].isin(filters["roles"])]
    role_matches = role_matches[role_matches["Roll_No"].isin(rolls)]

    st.subheader("Top 3 suitable roles per student")
    tops = (
        role_matches.sort_values("Match_Score", ascending=False)
        .groupby("Roll_No")
        .head(3)
        .copy()
    )
    tops["Student_Name"] = tops["Roll_No"].map(
        k["students"].set_index("Roll_No")["Student_Name"]
    )
    show = tops[["Student_Name", "Roll_No", "Role", "Match_Score", "Missing_Skills"]]
    st.dataframe(show.style.format({"Match_Score": "{:.1f}"}),
                 width="stretch", height=520)

    st.subheader("Average match score by role (batch)")
    avg = role_matches.groupby("Role")["Match_Score"].mean().sort_values()
    fig = px.bar(avg, x="Match_Score", y=avg.index, orientation="h",
                 color_discrete_sequence=[COLORS["navy"]],
                 title="Batch-average match score per role")
    st.plotly_chart(fig, width="stretch")

    with st.expander("Show full role-match matrix"):
        full = role_matches.copy()
        full["Student_Name"] = full["Roll_No"].map(
            k["students"].set_index("Roll_No")["Student_Name"]
        )
        st.dataframe(full[["Student_Name", "Roll_No", "Role", "Match_Score"]]
                     .pivot(index="Student_Name", columns="Role", values="Match_Score")
                     .style.background_gradient(cmap="Blues"),
                     width="stretch")


# ===========================================================================
# PAGE 6 - PROJECT QUESTIONS
# ===========================================================================
def page_questions():
    st.header("Final Project Questions & Answers")
    k = ANALYSIS

    st.subheader("Q1. What companies recruited students in the previous three years?")
    rec = k["placement"]["recruiters"]
    st.dataframe(rec, width="stretch")

    st.subheader("Q2. What were the most common job roles?")
    roles = k["placement"]["roles"].groupby("Role_Family")["Count"].sum().sort_values(ascending=False)
    st.write(", ".join(f"{i} ({c})" for i, c in roles.items()))

    st.subheader("Q3. What skills are most associated with these roles?")
    demand = k["placement"]["skill_demand"].head(12)
    st.dataframe(demand.reset_index(drop=True), width="stretch")

    st.subheader("Q4. How has the skill requirement changed over the three years?")
    hist = k["historical"].pivot(index="Skill", columns="Year", values="Average_Score")
    hist["Change"] = (hist[2026] - hist[2024]).round(2)
    hist = hist.sort_values("Change", ascending=False)
    st.dataframe(hist.reset_index(), width="stretch")

    st.subheader("Q5. What are the current skills of each 2027 student?")
    sm = k["score_matrix"]
    pos = sm[["Roll_No", "Student_Name"] + MASTER_SKILLS]
    st.dataframe(pos.style.background_gradient(cmap="Greens", axis=None), width="stretch", height=420)

    st.subheader("Q6. What is each student's individual skill gap?")
    g = k["gap_long"]
    st.dataframe(g, width="stretch", height=420)

    st.subheader("Q7. Which students have the highest training requirement?")
    ranked = summary.sort_values(["Num_Critical_Gaps", "Num_High_Gaps", "Overall_Gap"],
                                 ascending=False)
    st.dataframe(ranked[["Student_Name", "Roll_No", "CGPI", "Num_Critical_Gaps",
                         "Num_High_Gaps", "Overall_Gap", "Placement_Readiness"]],
                 width="stretch")

    st.subheader("Q8. Which skills are missing most commonly across the 2027 batch?")
    missing_common = (g[g["Gap"] > 0].groupby("Skill")["Roll_No"].nunique()
                      .sort_values(ascending=False).head(10))
    fig = px.bar(missing_common, x="Roll_No", y=missing_common.index, orientation="h",
                 title="Students with a gap per skill",
                 labels={"Roll_No": "Students with gap"})
    st.plotly_chart(fig, width="stretch")

    st.subheader("Q9. Which job roles is each student currently suitable for?")
    tops = (k["role_matches"].sort_values("Match_Score", ascending=False)
            .groupby("Roll_No").head(3))
    tops["Student_Name"] = tops["Roll_No"].map(
        k["students"].set_index("Roll_No")["Student_Name"])
    st.dataframe(tops[["Student_Name", "Role", "Match_Score", "Missing_Skills"]],
                 width="stretch", height=420)

    st.subheader("Q10. What skills should each student learn to improve placement readiness?")
    st.dataframe(k["recommendations"], width="stretch", height=420)


# ===========================================================================
# PAGE 7 - ACADEMIC CONCLUSION
# ===========================================================================
def page_conclusion():
    st.header("Final Academic Conclusion")
    st.markdown("The conclusion below is **computed from the calculated results** — "
                "nothing is hard-coded.")

    st.info("⚠️ " + SYNTHETIC_2026_NOTE)

    conclusion = report_mod.generate_conclusion(ANALYSIS)
    st.markdown(conclusion)

    st.divider()
    st.subheader("Key Aggregate Metrics")
    s = summary
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Students", len(s))
    c2.metric("Average CGPI", f"{s['CGPI'].mean():.2f}")
    c3.metric("Avg Skill Score", f"{s['Overall_Skill'].mean():.1f}")
    c4.metric("Avg Skill Gap", f"{s['Overall_Gap'].mean():.1f}")
    c5.metric("Avg Readiness", f"{s['Placement_Readiness'].mean():.1f}")
    c6.metric("Critical-Gap Students", int((s["Num_Critical_Gaps"] > 0).sum()))

    st.subheader("Readiness distribution")
    st.dataframe(s["Readiness_Level"].value_counts().rename("Students"), width="stretch")


# ===========================================================================
# PAGE 8 - EXPORTS
# ===========================================================================
def page_exports():
    st.header("Exports & Datasets")
    st.markdown(
        "All datasets are computed from the source records in `data/` and written to "
        "`outputs/` and `data/`."
    )

    files = [
        ("Student Skill Scores (CSV)", "outputs/student_skill_scores.csv"),
        ("Skill Gap Analysis (CSV)", "outputs/skill_gap_analysis.csv"),
        ("Placement Analysis (CSV)", "outputs/placement_analysis.csv"),
        ("Student Report (CSV)", "outputs/student_report.csv"),
        ("Role Match Scores (CSV)", "outputs/role_match_scores.csv"),
        ("Recommendations (CSV)", "outputs/recommendations.csv"),
        ("Skill Benchmark (CSV)", "outputs/skill_benchmark.csv"),
        ("Excel Workbook (all sheets)", "outputs/placement_skill_gap_analysis.xlsx"),
    ]

    for label, rel in files:
        path = ROOT / rel
        with open(path, "rb") as fh:
            st.download_button(label, fh.read(), file_name=path.name, key=rel)

    st.divider()
    st.subheader("Preview: Student Report (first rows)")
    st.dataframe(k_report().head(10), width="stretch")


@st.cache_data(show_spinner=False)
def k_report():
    return pd.read_csv(ROOT / "outputs" / "student_report.csv", keep_default_na=False)


# ===========================================================================
# PAGE 9 - ABOUT & METHODOLOGY
# ===========================================================================
def page_about():
    st.header("About & Methodology")
    st.markdown("""
**Project title:** Placement-Based Individual Skill Gap Analysis of 2027 IoT Batch
Students using the previous three years (2024, 2025, 2026) of placement data.

### Data sources
| Dataset | Source | Status |
| --- | --- | --- |
| Placement 2024 | College alumni records | Official |
| Placement 2025 | College alumni records | Official |
| Placement 2026 | **Synthetic/Demo data** | Demo only |
| Historical skill scores | Estimated analytical benchmark values | Demo only |
| 2027 student profiles | College profile PDF (`IOT.pdf`) | Primary source |

### Pipeline
```
Placement Data -> Role Analysis -> Skill Mapping -> Historical Benchmark
-> Student Skill Extraction -> Skill Scoring -> Gap Calculation
-> Role Matching -> Recommendation
```

### Scoring rubric (evidence-based, 0-5)
```
0 = Not mentioned        0
1 = Basic exposure      20
2 = Used in project     40
3 = Multiple projects / internship  60
4 = Strong evidence     80
5 = Advanced            100
```

### Formulas
* **Historical Benchmark** = (2024 + 2025 + 2026 score) / 3, computed dynamically.
* **Skill Gap** = Historical Benchmark - Student Skill Score (min 0).
* **Gap levels:** 0-5 Very Low | 5-10 Low | 10-20 Moderate | 20-30 High | 30+ Critical.
* **Overall Gap** = average gap over the skills required by the student's top-3
  matched job roles (irrelevant skills excluded).
* **Placement Readiness** = 100 - Overall Gap.
* **Role Match** = sum of student scores in role skills / max possible role score.

### Limitations
* 2026 placement data is **synthetic/demo**.
* Historical skill scores are **estimated** analytical values, not college measurements.
* Skill scores are based on the evidence available in student profiles.
* A skill gap does not guarantee a placement outcome; placements also depend on
  interview performance, aptitude, communication, market conditions and more.
""")

    st.divider()
    st.markdown(f"**2026 data note:** {SYNTHETIC_2026_NOTE}")


# ===========================================================================
# Router
# ===========================================================================
if page == PAGES[0]:
    page_overview()
elif page == PAGES[1]:
    page_gap_analysis()
elif page == PAGES[2]:
    page_heatmap()
elif page == PAGES[3]:
    page_profiles()
elif page == PAGES[4]:
    page_roles()
elif page == PAGES[5]:
    page_questions()
elif page == PAGES[6]:
    page_conclusion()
elif page == PAGES[7]:
    page_exports()
else:
    page_about()
