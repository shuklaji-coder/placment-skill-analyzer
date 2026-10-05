# Placement-Based Individual Skill Gap Analysis
## 2027 IoT Batch - Final Academic Report

### Scope
* Historical placement records: 2024, 2025 and 2026.
* 2026 data note: The 2026 placement record was not provided by the college. The 2026 dataset used in this project is SYNTHETIC/DEMO DATA generated for academic analysis and must NOT be treated as official college data.
* 2027 student profiles: extracted from the college profile PDF (36 students).

### Methodology
```
Placement Data -> Role Analysis -> Skill Mapping -> Historical Benchmark
-> Student Skill Extraction -> Skill Scoring -> Gap Calculation
-> Role Matching -> Recommendation
```

### Academic Conclusion (computed from results)
**Historical placement trend.** Over the previous three years the placement volume was 2024: 22, 2025: 20, 2026: 28 placements. 

The average offered salary moved across the years (2024: avg 4.1 LPA, 2025: avg 5.1 LPA, 2026: avg 4.6 LPA), showing an upward trend in entry-level compensation.

**Important placement skills.** Weighting the role-skill catalogue by how often each role family appeared in the placement records, the most demanded skills are: SQL, Python, Problem Solving, Git/GitHub, Java, DSA. These form the placement-ready skill baseline for the 2027 batch.

**Historical skill benchmark (mean of 2024-2026).** The strongest historical skill levels were Aptitude, CSS, Node.js, Express.js, JavaScript while SOC/SIEM, Network Security, Ethical Hacking, Cybersecurity, Linux were the weakest, indicating where the market benchmark is comparatively easier to meet.

**2027 batch skill distribution.** On average the batch is strongest in AI/ML, IoT, JavaScript, Python, CSS and weakest in Problem Solving, Spring Boot, Cryptography, Linux, SOC/SIEM.

**Major skill gaps.** Averaged across all students, the largest gaps against the historical benchmark are in Communication, Node.js, Figma, UI/UX, Problem Solving, REST API. These are the batch-level priorities for training intervention.

**Student-wise training requirements.** 36 student(s) have at least one critical skill gap and 0 more student(s) have high (but not critical) gaps. 

The students needing the most urgent training are: KOTIAN DHRUV, KOTIAN DAKSH, HOWALE RUDRA, HARALE ATHARV, MISHRA ANSH, JHA PALLAVI, JHA OMWARDHAN, YASH PARAB.

**Placement readiness.** After accounting for skill gaps, the readiness distribution of the batch is High Training Requirement: 30, Needs Improvement: 6.

**Most important training programs.** Aggregating the personalised recommendations, the most frequently prescribed topics are: NumPy, Pandas, Responsive Design, Indexing, OOP, SQL Queries, Joins, Subqueries.

**Potential placement improvement.** The average placement readiness of the batch is 46.2 (average overall skill score 11.0). Only 0% of students are currently Highly Placement Ready. If the identified critical and high skill gaps were closed through the recommended training programmes, the batch-level readiness would improve materially, giving students a stronger chance across the roles historically offered by recruiters.

### Key Aggregate Metrics

| Metric | Value |
| --- | --- |
| Total Students | 36 |
| Average CGPI | 8.3 |
| Average Overall Skill Score | 11.0 |
| Average Overall Skill Gap | 53.8 |
| Average Placement Readiness | 46.2 |
| Students with Critical Gaps | 36 |

### Files generated
* `outputs/student_skill_scores.csv` - student-wise skill matrix
* `outputs/skill_gap_analysis.csv` - student-skill gap matrix
* `outputs/placement_analysis.csv` - placement summary
* `outputs/student_report.csv` - per-student individual report
* `outputs/role_match_scores.csv` - student-to-role matching
* `outputs/recommendations.csv` - personalised training plans
* `outputs/placement_skill_gap_analysis.xlsx` - Excel workbook
* `data/skill_benchmark.csv` - dynamic historical benchmark
* `data/skill_gap_analysis.csv` - gap analysis dataset

---
*Report auto-generated. Synthetic 2026 data and estimated benchmarks are clearly labelled and must not be treated as official college records.*