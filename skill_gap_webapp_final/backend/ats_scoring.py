"""
ATS Score Module
==================
Computes a simple, explainable "ATS match score" the way most real
keyword-matching ATS tools actually work: the fraction of skills mentioned
in the job description that are also found in the resume.

This is deliberately NOT a black box — the score is just
(matched skills / total JD skills) * 100, because that's genuinely how the
keyword-screening layer of most real-world ATS software operates. We don't
claim to simulate any specific vendor's proprietary algorithm.
"""


def compute_ats_score(jd_skills, matched_skills):
    """
    jd_skills: list/set of skills extracted from the job description
    matched_skills: list/set of those JD skills also found in the resume

    Returns a dict with the numeric score, a human-readable label, and a
    short explanation of how it was computed (for transparency in the UI).
    """
    total = len(set(jd_skills))
    matched = len(set(matched_skills))

    if total == 0:
        return {
            "score": 0,
            "label": "Not enough data",
            "explanation": "No recognizable skills were found in the job description.",
        }

    score = round((matched / total) * 100)

    if score == 100:
        label = "Strong match"
    elif score >= 70:
        label = "Good match"
    elif score >= 40:
        label = "Moderate match"
    else:
        label = "Weak match"

    explanation = (
        f"{matched} of {total} skills mentioned in the job description "
        f"were found in the resume."
    )

    return {"score": score, "label": label, "explanation": explanation}


def build_fix_suggestions(missing_skills):
    """
    Turns each missing skill into a concrete, one-line actionable suggestion
    for improving the resume against this specific job description.
    """
    suggestions = []
    for skill in missing_skills:
        suggestions.append({
            "skill": skill,
            "suggestion": (
                f"Add \"{skill}\" to your resume — mention it in your skills "
                f"section, or better, in a work experience bullet that shows "
                f"how you've used it."
            ),
        })
    return suggestions


if __name__ == "__main__":
    jd_skills = {"Python", "SQL", "AWS", "Docker", "Machine Learning"}
    matched_skills = {"Python", "SQL", "Machine Learning"}
    missing_skills = jd_skills - matched_skills

    result = compute_ats_score(jd_skills, matched_skills)
    print("ATS score result:", result)

    fixes = build_fix_suggestions(sorted(missing_skills))
    print("\nFix suggestions:")
    for f in fixes:
        print(" -", f["suggestion"])
