import phonenumbers  # type: ignore

CANON_SKILLS = {
    "indesing": "Adobe InDesign",
    "teamwokz": "Teamworkz",
}


def canon_skill(s: str) -> str:
    k = (s or "").strip().lower()
    return CANON_SKILLS.get(k, (s or "").strip())


def normalize_contact(raw: dict) -> dict:
    out = dict(raw or {})
    phones = []
    for p in out.get("phones", []) or []:
        try:
            n = phonenumbers.parse(p, "ES")
            if phonenumbers.is_valid_number(n):
                phones.append(phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164))
        except Exception:
            continue
    if phones:
        out["phones"] = list(dict.fromkeys(phones))
    return out


def pick_candidate_name(cv: dict) -> str:
    cand = ((cv.get("candidate") or {}) or {}).get("name") if isinstance(cv.get("candidate"), dict) else None
    if cand:
        return cand
    for line in (cv.get("text") or "").splitlines()[:10]:
        s = (line or "").strip()
        if 3 <= len(s) <= 80 and "@" not in s and not s.isupper():
            if s.lower() not in ("microsoft office", "excel", "word", "photoshop", "indesign"):
                return s
    return ((cv.get("contact") or {}) or {}).get("name") or "No consta"


