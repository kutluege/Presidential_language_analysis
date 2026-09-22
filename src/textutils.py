"""Text helpers shared by inventory, preprocessing and chunking.

Everything here is pure and side-effect free. Nothing modifies files.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

WORD_RE = re.compile(r"\S+")
YEAR_RE = re.compile(r"\b(?:19[5-9]\d|20[0-4]\d)\b")

# --- artifact detectors -----------------------------------------------------------------------
HTML_RE = re.compile(r"<[a-zA-Z/][^>]{0,200}>|&(?:nbsp|amp|lt|gt|quot|#\d+);")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
TIMESTAMP_RE = re.compile(r"(?<![\d:])\d{1,2}:\d{2}(?::\d{2})?(?![\d:])")
STAGE_DIRECTION_RE = re.compile(
    r"[\[(]\s*(?:applause|laughter|laughs|music|cheers|cheering|inaudible|crosstalk|booing|chanting"
    r"|alkış|alkışlar|applaudissements|rires|beifall|applaus|lachen|аплодисменты)[^\])]{0,40}[\])]",
    re.I,
)
# "President of Russia Vladimir Putin:" / "MODERATOR:" style labels at line start.
# Every word must be Capitalised (or a small connector such as "of"), so ordinary sentence
# openers like "My fellow Americans:" or "Die einen sagen:" are not treated as labels.
_CAP = r"[A-ZÀ-ÝÇĞİÖŞÜ][\w.'’\-]*"
_CONNECTOR = r"(?:of|the|and|de|du|la|le|von|der|van|for)"
SPEAKER_LABEL_RE = re.compile(
    rf"^(?P<label>{_CAP}(?:\s+(?:{_CAP}|{_CONNECTOR})){{0,7}})\s*:\s+(?=\S)", re.M
)
INTERVIEWER_RE = re.compile(
    r"^(?:Q|A|Question|Answer|Interviewer|Moderator|Journalist|Reporter|Host|Soru|Cevap|Frage|Antwort)\s*[:.\-]",
    re.M | re.I,
)
# Third-person narration about the speaker (news commentary wrapped around a transcript).
THIRD_PERSON_RE = re.compile(
    r"\b(?:Putin|Trump|Macron|Merkel|Erdo[gğ]an|the president|the chancellor|le président|die Kanzlerin|Cumhurbaşkanı)\b"
    r"[^.\n]{0,40}\b(?:said|says|told|added|stated|declared|a déclaré|a dit|sagte|erklärte|dedi|söyledi|açıkladı)\b",
    re.I,
)
MULTI_SPACE_RE = re.compile(r"[^\S\n]{2,}")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+|(?<=[.!?…][\"”»)])\s+")

# --- tiny stopword lists for a dependency-free language guess -------------------------------
STOPWORDS: dict[str, frozenset[str]] = {
    "tr": frozenset(
        "ve bir bu için ile de da olarak çok daha en gibi kadar ama her biz bizim sizleri milletim olan şu ne "
        "mi mı değil var olsun ki tüm bütün ülkemiz milletimiz yıl yeni sizlere hepinizi bugün olduğu ise".split()
    ),
    "fr": frozenset(
        "le la les de des du et à un une nous vous que qui pour dans est sont ce cette ces avec sur pas plus "
        "notre nos sa ses au aux en il elle ils je mes chers compatriotes année France".split()
    ),
    "de": frozenset(
        "der die das und ist sind wir ich sie nicht ein eine den dem des mit für auf auch zu von im in es dass "
        "wie uns unsere unser sich haben werden an bei Jahr liebe Mitbürgerinnen Mitbürger Deutschland".split()
    ),
    "en": frozenset(
        "the and of to in a is are we our that for with this it on be have will as by you your not from all "
        "they their has at was were year new".split()
    ),
}


# --- reading ----------------------------------------------------------------------------------
def read_text(path: str | Path) -> tuple[str, str]:
    """Return (text, encoding_used). Normalizes line endings; never writes."""
    raw = Path(path).read_bytes()
    if not raw:
        return "", "empty"
    if raw.startswith(b"\xef\xbb\xbf"):
        text, enc = raw.decode("utf-8-sig"), "utf-8-sig"
    elif raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        text, enc = raw.decode("utf-16"), "utf-16"
    else:
        try:
            text, enc = raw.decode("utf-8"), "utf-8"
        except UnicodeDecodeError:
            text, enc = raw.decode("cp1252", errors="replace"), "cp1252(fallback)"
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text, enc


def split_paragraphs(text: str) -> list[str]:
    """Blank-line separated paragraphs, stripped, empties dropped."""
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def normalize_for_hash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


# --- language guess ---------------------------------------------------------------------------
def detect_language(text: str, min_ratio: float = 0.03) -> tuple[str, dict[str, float]]:
    tokens = [t.strip(".,;:!?…\"'“”«»()[]").lower() for t in WORD_RE.findall(text)]
    tokens = [t for t in tokens if t]
    if not tokens:
        return "unknown", {}
    lowered = {lang: {w.lower() for w in words} for lang, words in STOPWORDS.items()}
    scores = {lang: sum(1 for t in tokens if t in words) / len(tokens) for lang, words in lowered.items()}
    best = max(scores, key=scores.get)
    return (best if scores[best] >= min_ratio else "unknown"), scores


# --- duplicate detection ----------------------------------------------------------------------
def word_shingles(text: str, k: int = 8) -> set[str]:
    words = normalize_for_hash(text).split()
    if len(words) < k:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + k]) for i in range(len(words) - k + 1)}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def containment(a: set, b: set) -> float:
    """Share of the smaller set contained in the larger one (fragment detection)."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


# --- artifact scan ----------------------------------------------------------------------------
def repeated_lines(text: str, min_count: int = 3, min_chars: int = 15) -> list[tuple[str, int]]:
    counts = Counter(line.strip() for line in text.split("\n") if len(line.strip()) >= min_chars)
    return [(line, n) for line, n in counts.most_common() if n >= min_count]


def first_alpha_is_lower(text: str) -> bool:
    for ch in text.lstrip():
        if ch.isalpha():
            return ch.islower()
        if not ch.isspace() and ch not in "\"'“”«»([":
            return False
    return False


def scan_artifacts(text: str, inv_cfg: dict) -> list[tuple[str, str]]:
    """Return [(flag, detail)] for obvious non-speech artifacts. Detection only."""
    flags: list[tuple[str, str]] = []
    if not text.strip():
        return [("empty", "0 words")]

    if m := HTML_RE.findall(text):
        flags.append(("html_remnants", f"{len(m)} matches, e.g. {m[0]!r}"))
    if m := URL_RE.findall(text):
        flags.append(("urls", f"{len(m)} matches, e.g. {m[0]!r}"))
    if m := TIMESTAMP_RE.findall(text):
        flags.append(("timestamps", f"{len(m)} matches, e.g. {m[0]!r}"))
    if m := STAGE_DIRECTION_RE.findall(text):
        flags.append(("stage_directions", f"{len(m)} matches, e.g. {m[0]!r}"))
    if m := INTERVIEWER_RE.findall(text):
        flags.append(("interviewer_pattern", f"{len(m)} Q/A-style line starts"))

    labels = [x.group("label") for x in SPEAKER_LABEL_RE.finditer(text)]
    starts_with_label = bool(SPEAKER_LABEL_RE.match(text.lstrip()))
    if starts_with_label or len(labels) >= 3:
        flags.append(("speaker_label_prefix", f"{len(labels)} label(s), first: {labels[0]!r}"))

    if m := THIRD_PERSON_RE.findall(text):
        flags.append(("third_person_narration", f"{len(m)} sentence(s) narrate the speaker in third person"))

    rep = repeated_lines(text, inv_cfg.get("repeated_line_min_count", 3), inv_cfg.get("repeated_line_min_chars", 15))
    if rep:
        line, n = rep[0]
        flags.append(("repeated_lines", f"{len(rep)} distinct line(s) repeated >= {n}x, e.g. {line[:60]!r}"))

    if first_alpha_is_lower(text):
        flags.append(("truncated_start", f"text begins {text.lstrip()[:30]!r}"))

    n_multi = len(MULTI_SPACE_RE.findall(text))
    if n_multi >= inv_cfg.get("double_space_warn", 20):
        flags.append(("excess_whitespace", f"{n_multi} runs of multiple spaces (copy/paste or PDF artifact)"))

    return flags


def years_in_text(text: str) -> list[int]:
    return sorted({int(y) for y in YEAR_RE.findall(text)})
