"""Personalized training recommendation engine (Project Section 23).

For each student, skills with a High/Critical gap receive a tailored set of
training topics.  Skills with a Moderate gap receive a smaller focus list.
The recommended topics per skill follow the syllabus map defined below.
"""
import pandas as pd

# Skill -> ordered list of training topics (Project Section 23 + syllabus map)
TRAINING_TOPICS = {
    "DSA": ["Arrays", "Strings", "Linked Lists", "Stacks", "Queues", "Trees",
            "Graphs", "Dynamic Programming", "Problem Solving Practice"],
    "Cloud Computing": ["AWS", "EC2", "S3", "RDS", "Lambda", "IAM", "VPC", "Deployment"],
    "AWS": ["EC2", "S3", "RDS", "Lambda", "IAM", "VPC", "Deployment", "CloudWatch"],
    "Spring Boot": ["Spring Core", "Spring Boot", "REST API", "JPA/Hibernate",
                    "Spring Security", "PostgreSQL/MySQL", "Microservices Basics"],
    "React": ["JavaScript", "React", "Hooks", "State Management", "API Integration",
              "Responsive Design"],
    "AI/ML": ["Python", "NumPy", "Pandas", "Machine Learning", "Model Evaluation",
              "NLP", "Generative AI"],
    "Git/GitHub": ["Git", "GitHub", "Branching", "Pull Requests", "Merge",
                   "Conflict Resolution", "CI/CD Basics"],
    "SQL": ["SQL Queries", "Joins", "Subqueries", "Window Functions", "Indexing",
            "Database Design"],
    "DBMS": ["ER Diagrams", "Normalization", "Transactions", "Indexing", "SQL"],
    "Java": ["Core Java", "OOP", "Collections", "Multithreading", "Java 8",
             "Spring Framework"],
    "Python": ["Python Basics", "OOP", "NumPy", "Pandas", "Web Scraping", "Automation"],
    "C": ["Pointers", "Memory Management", "Structures", "File Handling"],
    "C++": ["STL", "OOP", "Templates", "Smart Pointers", "STL Algorithms"],
    "JavaScript": ["ES6+", "DOM Manipulation", "Async/Await", "Promises", "Closures"],
    "HTML": ["HTML5 Semantics", "Forms", "Accessibility", "SEO Basics"],
    "CSS": ["Flexbox", "Grid", "Responsive Design", "Animations", "Tailwind CSS"],
    "Node.js": ["Node.js", "Express", "REST APIs", "Authentication (JWT)",
                "MongoDB/Mongoose"],
    "REST API": ["HTTP Methods", "REST Design", "Postman", "Authentication",
                 "API Documentation"],
    "Full Stack": ["HTML/CSS", "JavaScript", "React", "Node.js/Express",
                   "MongoDB/SQL", "Deployment"],
    "Communication": ["Public Speaking", "Mock Interviews", "Group Discussions",
                      "Resume Writing", "Technical Presentation"],
    "Computer Networks": ["OSI Model", "TCP/IP", "DNS", "HTTP/HTTPS", "Subnetting",
                          "Routing & Switching"],
    "IoT": ["Arduino Programming", "ESP32", "Sensors & Actuators", "MQTT",
            "Edge-to-Cloud Integration", "ThingSpeak"],
    "Embedded Systems": ["C Programming", "Microcontrollers", "GPIO", "Interrupts",
                         "RTOS Basics", "PCB Design"],
    "Arduino": ["Arduino IDE", "Digital/Analog I/O", "Sensors Interfacing",
                "Serial Communication", "Embedded C"],
    "ESP32": ["ESP32 Setup", "WiFi/BLE", "MQTT Client", "Deep Sleep",
              "OTA Updates"],
    "Sensors": ["Temperature/Humidity Sensors", "IR/Ultrasonic Sensors",
                "Sensor Calibration", "Data Acquisition"],
    "MQTT": ["MQTT Protocol", "Brokers (Mosquitto)", "Topics & QoS", "Publish/Subscribe"],
    "Hardware Integration": ["Sensor Interfacing", "GPIO", "I2C/SPI/UART",
                             "Power Management"],
    "Cybersecurity": ["Networking Basics", "Linux", "Security Tools (Nmap, Wireshark)",
                      "SOC/SIEM", "Cryptography", "Vulnerability Assessment"],
    "Cryptography": ["Symmetric/Asymmetric Encryption", "Hashing", "PKI", "SSL/TLS",
                     "Digital Signatures"],
    "Linux": ["Linux Commands", "Shell Scripting", "File Permissions",
              "Process Management", "Networking Tools"],
    "SOC/SIEM": ["SIEM Tools (Splunk, Wazuh)", "Log Analysis", "Incident Response",
                 "Threat Detection", "SOAR Basics"],
    "OOP": ["Classes & Objects", "Inheritance", "Polymorphism", "Abstraction",
            "Encapsulation"],
    "Problem Solving": ["Logical Reasoning", "Algorithm Design", "Coding Practice",
                        "Puzzle Solving"],
    "Data Science": ["Python", "NumPy", "Pandas", "Data Cleaning", "Visualization",
                     "Statistical Analysis"],
    "Data Analytics": ["Excel", "SQL", "Power BI", "Tableau", "Data Storytelling",
                       "Dashboards"],
    "UI/UX": ["UI/UX Principles", "Figma", "Design Systems", "Prototyping",
              "Responsive Design"],
    "Figma": ["Figma Basics", "Components", "Auto Layout", "Prototyping",
              "Design Collaboration"],
    "Aptitude": ["Quantitative Aptitude", "Logical Reasoning", "Verbal Ability",
                 "Speed Maths", "Mock Tests"],
    "Teamwork": ["Collaboration", "Agile Basics", "Peer Review", "Open Source Contribution"],
    "FastAPI": ["Python", "FastAPI Basics", "REST APIs", "Pydantic", "SQLAlchemy"],
    "Django": ["Django Basics", "ORM", "Authentication", "REST Framework"],
    "TypeScript": ["TypeScript Basics", "Types & Interfaces", "Generics", "React + TS"],
    "Kotlin": ["Kotlin Basics", "Coroutines", "Jetpack Compose", "Android Development"],
    "Android": ["Android Studio", "Activities & Fragments", "Jetpack Compose",
                "Room Database", "Networking"],
    "Flutter": ["Flutter Widgets", "Dart", "State Management", "Firebase", "Publishing"],
    "Dart": ["Dart Basics", "Collections", "Async Programming", "OOP in Dart"],
    "Network Security": ["Firewalls", "IDS/IPS", "Penetration Testing Basics",
                         "Security Monitoring"],
    "Ethical Hacking": ["Reconnaissance", "Scanning", "Exploitation Basics",
                        "Post-Exploitation", "Bug Bounty Platforms"],
    "Generative AI": ["Prompt Engineering", "LLM APIs", "RAG Basics", "Fine-tuning",
                      "AI Safety"],
    "NLP": ["Tokenization", "Text Preprocessing", "Word Embeddings", "Transformers"],
    "Prompt Engineering": ["Prompt Design", "Few-shot Learning", "Chain-of-Thought",
                           "Evaluation"],
    "Docker": ["Docker Basics", "Images & Containers", "Docker Compose", "Dockerfile"],
    "CI/CD": ["CI/CD Concepts", "GitHub Actions", "Jenkins", "Pipeline Design"],
    "Kubernetes": ["Kubernetes Basics", "Pods & Deployments", "Services", "Helm"],
    "Azure": ["Azure Fundamentals", "Azure VMs", "Azure Functions", "Storage"],
    "Google Cloud": ["GCP Core Services", "Compute Engine", "Cloud Functions",
                     "Cloud Storage"],
    "Next.js": ["Next.js Routing", "SSR/SSG", "API Routes", "Deployment"],
    "Express.js": ["Express Routing", "Middleware", "REST APIs", "Error Handling"],
    "Raspberry Pi": ["Pi Setup", "GPIO Programming", "Home Automation", "Pi OS"],
    "PCB": ["Schematic Design", "PCB Layout", "KiCad", "Design for Manufacture"],
}

DEFAULT_TOPICS = ["Fundamentals", "Hands-on Practice", "Build Projects",
                  "Mock Tests & Assessments"]

GAP_PRIORITY = {
    "Critical Gap": "Priority 1 - Urgent (Critical Gap)",
    "High Gap": "Priority 2 - High (High Gap)",
    "Moderate Gap": "Priority 3 - Moderate (Moderate Gap)",
    "Low Gap": "Priority 4 - Low (Low Gap)",
    "Very Low / No Gap": "Priority 5 - Low (Very Low / No Gap)",
}


def topics_for_skill(skill):
    return TRAINING_TOPICS.get(skill, DEFAULT_TOPICS)


def build_recommendations(gap_long, role_matches, per_student_skills=None):
    """Long table: Roll_No, Skill, Gap, Gap_Level, Priority, Recommended_Topics,
    Suggested_Roles.

    Only skills with a Moderate/High/Critical gap receive recommendations.  When
    per_student_skills is provided, recommendations are scoped to each student's
    relevant (target-role) skill set so the plan stays role-focused.
    """
    rows = []
    target_gap = gap_long[gap_long["Gap_Level"].isin(["Critical Gap", "High Gap", "Moderate Gap"])]
    for _, g in target_gap.iterrows():
        if per_student_skills is not None:
            relevant = set(per_student_skills.get(g["Roll_No"], []))
            if g["Skill"] not in relevant:
                continue
        best_role = _best_role_for(g["Roll_No"], role_matches)
        rows.append({
            "Roll_No": g["Roll_No"],
            "Student_Name": g["Student_Name"],
            "Skill": g["Skill"],
            "Gap": g["Gap"],
            "Gap_Level": g["Gap_Level"],
            "Priority": GAP_PRIORITY[g["Gap_Level"]],
            "Recommended_Topics": "; ".join(topics_for_skill(g["Skill"])),
            "Suggested_Target_Role": best_role,
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["Roll_No", "Gap"], ascending=[True, False]).reset_index(drop=True)
    return df


def student_training_plan(gap_long, role_matches, roll_no, per_student_skills=None):
    """Friendly per-student training plan (list of dicts) for the profile page."""
    sub = gap_long[(gap_long["Roll_No"] == roll_no) &
                   (gap_long["Gap_Level"].isin(["Critical Gap", "High Gap", "Moderate Gap"]))]
    if per_student_skills is not None:
        relevant = set(per_student_skills.get(roll_no, []))
        sub = sub[sub["Skill"].isin(relevant)]
    sub = sub.sort_values("Gap", ascending=False)
    plan = []
    for _, g in sub.iterrows():
        plan.append({
            "skill": g["Skill"],
            "gap": g["Gap"],
            "level": g["Gap_Level"],
            "topics": topics_for_skill(g["Skill"]),
        })
    return plan


def _best_role_for(roll_no, role_matches):
    sub = role_matches[role_matches["Roll_No"] == roll_no]
    if sub.empty:
        return "General Placement Prep"
    return sub.sort_values("Match_Score", ascending=False).iloc[0]["Role"]
