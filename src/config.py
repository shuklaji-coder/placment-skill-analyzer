"""Project-wide constants and configuration.

This module defines the master skill catalogue, skill categories, the
keyword rules used to normalise raw student evidence into master skills,
and the job-role -> required-skill mapping used for role matching.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Data files (source / input)
PLACEMENT_FILES = {
    2024: DATA_DIR / "placement_2024.csv",
    2025: DATA_DIR / "placement_2025.csv",
    2026: DATA_DIR / "placement_2026_demo.csv",
}
STUDENTS_FILE = DATA_DIR / "students_2027.csv"
HISTORICAL_SKILLS_FILE = DATA_DIR / "historical_skills.csv"
ROLE_SKILL_MAP_FILE = DATA_DIR / "role_skill_map.csv"

# Data files (calculated / output, saved for reference)
SKILL_BENCHMARK_FILE = DATA_DIR / "skill_benchmark.csv"
SKILL_GAP_ANALYSIS_FILE = DATA_DIR / "skill_gap_analysis.csv"

# Output files (exports)
OUTPUT_FILES = {
    "student_scores": OUTPUTS_DIR / "student_skill_scores.csv",
    "skill_gap": OUTPUTS_DIR / "skill_gap_analysis.csv",
    "placement": OUTPUTS_DIR / "placement_analysis.csv",
    "report": OUTPUTS_DIR / "student_report.csv",
    "role_match": OUTPUTS_DIR / "role_match_scores.csv",
    "recommendations": OUTPUTS_DIR / "recommendations.csv",
    "benchmark": OUTPUTS_DIR / "skill_benchmark.csv",
    "excel": OUTPUTS_DIR / "placement_skill_gap_analysis.xlsx",
}
FINAL_REPORT_FILE = REPORTS_DIR / "final_report.md"

# ---------------------------------------------------------------------------
# Synthetic / demo data label
# ---------------------------------------------------------------------------
SYNTHETIC_2026_LABEL = "Synthetic/Demo Placement Data for Academic Analysis"
SYNTHETIC_2026_NOTE = (
    "The 2026 placement record was not provided by the college. "
    "The 2026 dataset used in this project is SYNTHETIC/DEMO DATA generated for "
    "academic analysis and must NOT be treated as official college data."
)

# ---------------------------------------------------------------------------
# Master skill catalogue grouped into categories (Project Section 11)
# ---------------------------------------------------------------------------
SKILL_CATEGORIES = {
    "Programming": ["Java", "Python", "C", "C++", "JavaScript", "TypeScript", "Kotlin", "Dart"],
    "Core CS": ["DSA", "OOP", "DBMS", "SQL", "Computer Networks", "Operating Systems", "Problem Solving"],
    "Web": ["HTML", "CSS", "React", "Node.js", "Express.js", "Next.js", "REST API", "Full Stack"],
    "Backend": ["Spring Boot", "FastAPI", "Django"],
    "Mobile": ["Android", "Flutter"],
    "Cloud / DevOps": ["AWS", "Azure", "Google Cloud", "Docker", "CI/CD", "Kubernetes", "Cloud Computing", "Git/GitHub"],
    "AI / Data": ["AI/ML", "Data Science", "Data Analytics", "Generative AI", "NLP", "Prompt Engineering"],
    "IoT / Embedded": ["IoT", "Arduino", "ESP32", "Raspberry Pi", "Embedded Systems", "Sensors", "MQTT", "PCB", "Hardware Integration"],
    "Cybersecurity": ["Cybersecurity", "Ethical Hacking", "Cryptography", "Linux", "SOC/SIEM", "Network Security"],
    "Other Placement Skills": ["Communication", "Teamwork", "Aptitude", "UI/UX", "Figma"],
}

# Flattened master skill list (order matters: used as matrix columns).
MASTER_SKILLS = [skill for skills in SKILL_CATEGORIES.values() for skill in skills]

# ---------------------------------------------------------------------------
# Historical skill -> master skill mapping.
# The provided historical skill names are grouped; every master skill inherits
# the benchmark of the historical skill group it belongs to.
# ---------------------------------------------------------------------------
HISTORICAL_GROUP_MAP = {
    "Java": ["Java"],
    "Python": ["Python"],
    "SQL": ["SQL", "DBMS"],
    "DSA": ["DSA", "OOP", "Problem Solving"],
    "Web Development": ["HTML", "CSS", "JavaScript", "Node.js", "Express.js", "Next.js",
                         "REST API", "Full Stack", "UI/UX", "Figma"],
    "Spring Boot": ["Spring Boot", "FastAPI", "Django"],
    "React": ["React"],
    "Cloud/DevOps": ["Cloud Computing", "AWS", "Azure", "Google Cloud", "Docker", "CI/CD", "Kubernetes"],
    "AI/ML": ["AI/ML", "Data Science", "Data Analytics", "Generative AI", "NLP", "Prompt Engineering"],
    "Communication": ["Communication", "Teamwork"],
    "Aptitude": ["Aptitude"],
    "Git/GitHub": ["Git/GitHub"],
    "IoT/Embedded": ["IoT", "Arduino", "ESP32", "Raspberry Pi", "Embedded Systems",
                     "Sensors", "MQTT", "PCB", "Hardware Integration"],
    "Cybersecurity": ["Cybersecurity", "Ethical Hacking", "Cryptography", "Linux", "SOC/SIEM", "Network Security"],
}

# ---------------------------------------------------------------------------
# Keyword rules: master skill -> list of regex patterns.
# Patterns are matched (case-insensitive) against the lower-cased raw strings
# of a student's Technical_Skills, Projects, Internships and Certifications.
# ---------------------------------------------------------------------------
SKILL_KEYWORDS = {
    # ---- Programming ----
    "Java": [r"\bjava\b", r"j2ee"],
    "Python": [r"\bpython\b"],
    "C": [r"\bc\b"],
    "C++": [r"c\+\+", r"\bcpp\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b", r"\bes6", r"web development", r"web dev", r"\bwebsite\b",
                  r"frontend", r"front-end", r"web app", r"web page", r"web clock", r"front end"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "Kotlin": [r"\bkotlin\b", r"\bktor\b", r"kotlin multiplatform"],
    "Dart": [r"\bdart\b", r"\bflutter\b"],
    # ---- Core CS ----
    "DSA": [r"\bdsa\b", r"data structure", r"data structures", r"\balgorithm\b", r"algorithms", r"leetcode"],
    "OOP": [r"\boop\b", r"\boops\b", r"object.orient", r"clean architecture", r"software engineering"],
    "DBMS": [r"\bdbms\b", r"database management", r"\bmongodb\b", r"\bnosql\b", r"datastore",
             r"firestore", r"realtime database", r"real-time database", r"room database",
             r"\bcrud\b", r"\bmysql\b", r"postgres", r"postgresql", r"sql server", r"microsoft sql", r"\bsql\b"],
    "SQL": [r"\bsql\b", r"mysql", r"postgres", r"postgresql", r"sql server", r"microsoft sql", r"\bdbms\b"],
    "Computer Networks": [r"computer network", r"computer networking", r"\bnetworking\b", r"\bnetwork\b",
                          r"tcp/ip", r"tcp ip", r"\bvpc\b", r"\bsubnet", r"cisco packet tracer",
                          r"\bcisco\b", r"socket"],
    "Operating Systems": [r"operating system", r"\bos\b", r"\blinux\b", r"\bvmware\b", r"virtualization"],
    "Problem Solving": [r"problem.solving", r"problem solving"],
    # ---- Web ----
    "HTML": [r"\bhtml\b", r"web development", r"web dev", r"\bwebsite\b", r"web page", r"web app",
             r"web clock", r"frontend", r"front-end", r"front end"],
    "CSS": [r"\bcss\b", r"tailwind", r"bootstrap", r"web development", r"web dev", r"\bwebsite\b",
            r"web page", r"web app", r"web clock", r"frontend", r"front-end", r"front end"],
    "React": [r"\breact\b", r"reactjs", r"react\.js", r"nextjs", r"next\.js", r"next js"],
    "Node.js": [r"\bnode\b", r"\bnodejs\b", r"node\.js", r"node backend"],
    "Express.js": [r"\bexpress\b", r"expressjs", r"express\.js", r"express js"],
    "Next.js": [r"nextjs", r"next\.js", r"next js"],
    "REST API": [r"\bapi\b", r"\bapis\b", r"restful", r"\brest\b", r"web api", r"api integration",
                 r"api call", r"retrofit", r"postman", r"api gateway"],
    "Full Stack": [r"full.?stack", r"\bmern\b", r"\bpern\b", r"frontend", r"front-end", r"front end",
                   r"backend", r"back.end", r"fullstack"],
    # ---- Backend ----
    "Spring Boot": [r"\bspring\b", r"spring boot", r"\bboot\b", r"java backend"],
    "FastAPI": [r"fastapi", r"fast api"],
    "Django": [r"\bdjango\b"],
    # ---- Mobile ----
    "Android": [r"\bandroid\b", r"android studio", r"mobile app", r"mobile application", r"mobile development",
                r"cross.platform app", r"android development", r"android app"],
    "Flutter": [r"\bflutter\b"],
    # ---- Cloud / DevOps ----
    "AWS": [r"\baws\b", r"amazon web", r"\bec2\b", r"\bs3\b", r"\blambda\b", r"\brds\b", r"dynamodb",
            r"eventbridge", r"\bsns\b", r"cloudfront", r"cloud practitioner", r"api gateway",
            r"amazon ec2", r"amazon s3"],
    "Azure": [r"\bazure\b"],
    "Google Cloud": [r"google cloud", r"\bgcp\b"],
    "Docker": [r"\bdocker\b", r"\bcontainer\b"],
    "CI/CD": [r"ci/cd", r"cicd", r"ci cd", r"continuous integration", r"continuous deployment"],
    "Kubernetes": [r"kubernetes", r"k8s"],
    "Cloud Computing": [r"cloud", r"cloud computing", r"cloud integration", r"cloud services", r"devops",
                        r"cloud and remote computing", r"cloud computation"],
    "Git/GitHub": [r"\bgit\b", r"\bgithub\b"],
    # ---- AI / Data ----
    "AI/ML": [r"ai/ml", r"aiml", r"ai and ml", r"ai & ml", r"ai&ml", r"machine learning", r"\bml\b",
              r"artificial intelligence", r"\bai\b", r"deep learning", r"\bnlp\b", r"data science",
              r"sentiment", r"agentic ai"],
    "Data Science": [r"data science", r"data scientist"],
    "Data Analytics": [r"data analytics", r"data analyst", r"data analysis", r"\banalytics\b",
                       r"power ?bi", r"\btableau\b", r"data visualization"],
    "Generative AI": [r"generative ai", r"genai", r"gen ai", r"\bllm\b", r"\bgenerative\b"],
    "NLP": [r"\bnlp\b", r"natural language", r"sentiment"],
    "Prompt Engineering": [r"prompt engineer", r"prompt engineering"],
    # ---- IoT / Embedded ----
    "IoT": [r"\biot\b", r"internet of things", r"\besp32\b", r"\besp\b", r"arduino", r"raspberry",
            r"\bsensor\b", r"sensors", r"telemetry", r"\bmqtt\b", r"iot development", r"iot system",
            r"thingspeak", r"embedded", r"iot intern", r"iot-based", r"iot based", r"iot smart",
            r"internet of things (iot)"],
    "Arduino": [r"arduino", r"\buno\b"],
    "ESP32": [r"\besp32\b", r"\besp\b"],
    "Raspberry Pi": [r"raspberry"],
    "Embedded Systems": [r"embedded", r"embedded systems", r"embedded programming", r"embedded system",
                         r"microcontroller", r"firmware", r"embedded systems intern"],
    "Sensors": [r"\bsensor\b", r"sensors", r"actuator", r"actuators", r"sensor-based", r"sensor based",
                r"sensor & actuator"],
    "MQTT": [r"\bmqtt\b"],
    "PCB": [r"\bpcb\b", r"pcb design", r"kicad", r"pcb designing"],
    "Hardware Integration": [r"hardware", r"hardware integration", r"microcontroller", r"hardware integration ide"],
    # ---- Cybersecurity ----
    "Cybersecurity": [r"cyber", r"cybersecurity", r"cyber security", r"secuirty", r"security",
                      r"\bsoc\b", r"\bsiem\b", r"ethical hack", r"\bhacking\b", r"fortinet",
                      r"intrusion detection", r"deepfake", r"vulnerability"],
    "Ethical Hacking": [r"ethical hack", r"\bhacking\b", r"kali linux", r"\bhacker\b"],
    "Cryptography": [r"cryptograph", r"\bcrypto\b"],
    "Linux": [r"\blinux\b", r"kali linux", r"\bkali\b"],
    "SOC/SIEM": [r"\bsoc\b", r"\bsiem\b", r"soc/siem"],
    "Network Security": [r"network security", r"cybersecurity", r"cyber security", r"\bsecurity\b",
                         r"intrusion detection"],
    # ---- Other Placement Skills ----
    "Communication": [r"communication", r"public speaking", r"soft skills", r"debating", r"presentation"],
    "Teamwork": [r"teamwork", r"\bteam\b"],
    "Aptitude": [r"aptitude", r"\bquant\b", r"reasoning", r"logical"],
    "UI/UX": [r"\bui\b", r"\bux\b", r"ui/ux", r"ui ux", r"\bdesign\b", r"responsive", r"graphic designing",
              r"canva", r"affinity"],
    "Figma": [r"\bfigma\b"],
}

# ---------------------------------------------------------------------------
# Scoring scale (Project Section 13)
# ---------------------------------------------------------------------------
LEVEL_TO_SCORE = {0: 0, 1: 20, 2: 40, 3: 60, 4: 80, 5: 100}

# ---------------------------------------------------------------------------
# Gap classification thresholds (Project Section 15)
# ---------------------------------------------------------------------------
GAP_CLASSES = [
    (30.0, "Critical Gap"),
    (20.0, "High Gap"),
    (10.0, "Moderate Gap"),
    (5.0, "Low Gap"),
    (0.0, "Very Low / No Gap"),
]

# Readiness classification (Project Section 17)
READINESS_CLASSES = [
    (80.0, "Highly Placement Ready"),
    (65.0, "Placement Ready"),
    (50.0, "Needs Improvement"),
    (0.0, "High Training Requirement"),
]


def classify_gap(gap):
    """Classify a numeric gap into a level (Project Section 15)."""
    if gap is None or (isinstance(gap, float) and gap != gap):  # NaN
        return "NA"
    for threshold, label in GAP_CLASSES:
        if gap >= threshold:
            return label
    return "Very Low / No Gap"


def classify_readiness(score):
    """Classify a placement readiness score (Project Section 17)."""
    if score is None or (isinstance(score, float) and score != score):  # NaN
        return "NA"
    for threshold, label in READINESS_CLASSES:
        if score >= threshold:
            return label
    return "High Training Requirement"
