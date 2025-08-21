from typing import Dict, Any


WEIGHTS = {
    "experience": 0.30,
    "education": 0.15,
    "languages": 0.10,
    "tools": 0.15,
    "contact": 0.10,
    "structure": 0.20,
}


def _bin(val, thresholds):  # thresholds = [(<=t,score), ...]
    for t, score in thresholds:
        if val <= t:
            return score
    return thresholds[-1][1]


def score_experience(years=None, roles=None):
    if years is not None:
        return _bin(years, [(0, 1), (1, 2), (2, 3), (3, 4), (5, 5)])
    n = roles or 0
    return _bin(n, [(0, 1), (1, 2), (2, 3), (3, 4), (5, 5)])


def score_education(n):
    return _bin(n, [(0, 1), (1, 2), (2, 3), (4, 4), (5, 5)])


def score_languages(n):
    return _bin(n, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)])


def score_tools(n):
    return _bin(n, [(0, 1), (1, 2), (3, 3), (5, 4), (6, 5)])


def score_contact(email, phone, location, linkedin):
    pts = int(bool(email)) + int(bool(phone)) + int(bool(location)) + int(bool(linkedin))
    return [1, 2, 3, 4, 5][pts] if pts < 5 else 5


def score_structure(has_summary, has_chronology, has_exp, has_edu, has_sections):
    pts = sum([has_summary, has_chronology, has_exp, has_edu, has_sections])
    return [1, 2, 3, 4, 5][pts] if pts < 5 else 5


def compute_cv_analysis(cv: Dict[str, Any]) -> Dict[str, Any]:
    years = cv.get("experience_years")
    roles = len(cv.get("experience", []) or [])
    edu_n = len(cv.get("education", []) or [])
    lang_n = len(cv.get("languages", []) or [])
    tools_n = len(set(cv.get("skills", []) or []))
    contact = cv.get("contact") or {}
    s_contact = score_contact(contact.get("emails"), contact.get("phones"), contact.get("location"), contact.get("linkedin"))

    structure_flags = dict(
        has_summary=bool(cv.get("summary")),
        has_chronology=roles >= 2,
        has_exp=roles >= 1,
        has_edu=edu_n >= 1,
        has_sections=bool(cv.get("sections")),
    )
    s = {
        "experience": score_experience(years, roles),
        "education": score_education(edu_n),
        "languages": score_languages(lang_n),
        "tools": score_tools(tools_n),
        "contact": s_contact,
        "structure": score_structure(**structure_flags),
    }
    overall = round(sum(s[k] * WEIGHTS[k] for k in WEIGHTS))
    return {
        "dimensions": [{"id": k, "label": k.capitalize(), "score": int(v)} for k, v in s.items()],
        "overall": {"score": int(overall)},
        "evidence": {
            "years": years,
            "roles": roles,
            "edu_n": edu_n,
            "lang_n": lang_n,
            "tools_n": tools_n,
            "contact": {k: bool(contact.get(k)) for k in ("emails", "phones", "location", "linkedin")},
            "structure": structure_flags,
        },
    }


