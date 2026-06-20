"""
Skills Taxonomy Module
=======================
Defines the master skill universe used across the Skill-Gap Prediction System:
- Skill categories and individual skills
- Role -> required skill mappings (ground truth for job descriptions)
- Skill co-occurrence / relatedness (used for learning path sequencing)

This taxonomy acts as the controlled vocabulary that the NLP extraction
pipeline matches free text against, and that the recommendation engine
uses to build learning paths.
"""

SKILL_TAXONOMY = {
    "Programming Languages": [
        "Python", "Java", "C++", "JavaScript", "SQL", "R", "Go", "TypeScript", "Scala"
    ],
    "Data Science & ML": [
        "Machine Learning", "Deep Learning", "Natural Language Processing",
        "Computer Vision", "Statistics", "Data Visualization", "Feature Engineering",
        "Model Deployment", "MLOps", "Reinforcement Learning", "Time Series Analysis"
    ],
    "ML/DS Libraries & Frameworks": [
        "scikit-learn", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Keras",
        "XGBoost", "Hugging Face Transformers", "OpenCV"
    ],
    "Data Engineering": [
        "ETL Pipelines", "Apache Spark", "Apache Airflow", "Data Warehousing",
        "Kafka", "Hadoop", "Data Modeling", "dbt"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "Google Cloud Platform", "Docker", "Kubernetes",
        "CI/CD", "Terraform", "Linux", "Git"
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Oracle DB"
    ],
    "Web Development": [
        "React", "Node.js", "Django", "Flask", "REST API Design", "HTML/CSS", "FastAPI"
    ],
    "Soft Skills": [
        "Communication", "Stakeholder Management", "Agile/Scrum", "Problem Solving",
        "Team Leadership", "Project Management", "Technical Writing", "Mentoring"
    ],
    "Business & Analytics": [
        "Business Intelligence", "A/B Testing", "Data Storytelling", "Tableau",
        "Power BI", "Excel", "Product Analytics", "KPI Design"
    ],
}

# Flat lookup of every skill -> category
SKILL_TO_CATEGORY = {
    skill: category
    for category, skills in SKILL_TAXONOMY.items()
    for skill in skills
}

ALL_SKILLS = sorted(SKILL_TO_CATEGORY.keys())

# ---------------------------------------------------------------------------
# Target roles and their "ground truth" required skills.
# Each role has core (must-have) and bonus (nice-to-have) skills.
# This is used to synthesize realistic job descriptions and to evaluate
# candidate skill gaps against a target role.
# ---------------------------------------------------------------------------
ROLE_SKILL_REQUIREMENTS = {
    "Data Scientist": {
        "core": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas",
                 "NumPy", "scikit-learn", "Data Visualization", "Feature Engineering"],
        "bonus": ["Deep Learning", "TensorFlow", "PyTorch", "AWS", "A/B Testing",
                  "Communication", "Data Storytelling", "XGBoost"],
    },
    "Machine Learning Engineer": {
        "core": ["Python", "Machine Learning", "Deep Learning", "TensorFlow",
                 "PyTorch", "Model Deployment", "MLOps", "Docker", "Git"],
        "bonus": ["Kubernetes", "AWS", "CI/CD", "Apache Spark", "Feature Engineering",
                  "Hugging Face Transformers", "Computer Vision"],
    },
    "Data Analyst": {
        "core": ["SQL", "Excel", "Data Visualization", "Tableau", "Power BI",
                 "Statistics", "Business Intelligence"],
        "bonus": ["Python", "A/B Testing", "Data Storytelling", "Product Analytics",
                  "KPI Design", "Communication"],
    },
    "Data Engineer": {
        "core": ["Python", "SQL", "ETL Pipelines", "Apache Spark", "Apache Airflow",
                 "Data Warehousing", "Data Modeling", "Git"],
        "bonus": ["Kafka", "Hadoop", "AWS", "Docker", "Kubernetes", "dbt", "Scala"],
    },
    "AI Research Engineer": {
        "core": ["Python", "Deep Learning", "PyTorch", "Machine Learning",
                 "Natural Language Processing", "Statistics", "Reinforcement Learning"],
        "bonus": ["Hugging Face Transformers", "Computer Vision", "TensorFlow",
                  "Technical Writing", "Time Series Analysis"],
    },
    "Backend Software Engineer": {
        "core": ["Python", "Java", "SQL", "REST API Design", "Git", "Docker",
                 "PostgreSQL", "Linux"],
        "bonus": ["Kubernetes", "AWS", "Kafka", "Redis", "CI/CD", "FastAPI", "Django"],
    },
    "Analytics Manager": {
        "core": ["SQL", "Business Intelligence", "Stakeholder Management",
                 "Team Leadership", "Data Storytelling", "Project Management"],
        "bonus": ["Python", "Tableau", "Power BI", "A/B Testing", "Communication",
                  "KPI Design", "Mentoring"],
    },
}

ALL_ROLES = sorted(ROLE_SKILL_REQUIREMENTS.keys())

# ---------------------------------------------------------------------------
# Skill relatedness graph: which skills are natural prerequisites/co-learned.
# Used by the recommendation engine to sequence a learning path rather than
# returning an unordered list of gaps.
# ---------------------------------------------------------------------------
SKILL_PREREQUISITES = {
    "Deep Learning": ["Machine Learning", "Python"],
    "TensorFlow": ["Python", "Machine Learning"],
    "PyTorch": ["Python", "Machine Learning"],
    "MLOps": ["Machine Learning", "Docker", "Git"],
    "Model Deployment": ["Machine Learning", "Docker"],
    "Kubernetes": ["Docker"],
    "Computer Vision": ["Deep Learning", "Python"],
    "Natural Language Processing": ["Machine Learning", "Python"],
    "Hugging Face Transformers": ["Deep Learning", "Natural Language Processing"],
    "Apache Airflow": ["Python", "ETL Pipelines"],
    "Apache Spark": ["Python", "SQL"],
    "dbt": ["SQL", "Data Modeling"],
    "CI/CD": ["Git", "Docker"],
    "FastAPI": ["Python", "REST API Design"],
    "Django": ["Python", "REST API Design"],
    "XGBoost": ["Machine Learning", "Python"],
    "A/B Testing": ["Statistics"],
}
