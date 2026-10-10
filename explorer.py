# explorer.py - the only module in this project that calls a language model.
#
# main.py imports this module, but no call happens at import time, so check.py
# and diag.py still cost nothing to run.
#
# Spec sections implemented here: 8 (the explorer sets its own question, then
# may only look for answers inside it), 10 (the five end states, amendment A2),
# 13 (the model never touches a number).
#
# No HTTP library beyond the standard one. The endpoint is OpenAI-compatible,
# so a plain POST is all it takes, and that removes one dependency whose major
# version could change under us on a redeploy.

import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.tokenfactory.nebius.com/v1"

# Both IDs came from client.models.list(). The capitalisation rules differ
# between them and neither is guessable - do not retype these from memory.
EXPLORER_MODEL = "nvidia/nemotron-3-super-120b-a12b"
REVIEWER_MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"

# Nemotron reasons before it answers, and the reasoning is billed against the
# same budget as the answer. A small max_tokens returns an empty string because
# the whole allowance went into thinking.
MAX_TOKENS = 4096
TIMEOUT = 120

# ---------------------------------------------------------------------------
# The five states a research direction can end in - spec section 10.
#
# PENDING is not one of them. The five are end states; PENDING says research
# has not run yet, which is the honest label between the explorer finishing and
# the evidence layer starting.
# ---------------------------------------------------------------------------

RESULT = "RESULT"
NO_EVIDENCE = "NO_EVIDENCE"
RESEARCH_INCOMPLETE = "RESEARCH_INCOMPLETE"
EVENT_OUTSIDE_MEASURABLE_RANGE = "EVENT_OUTSIDE_MEASURABLE_RANGE"
EVIDENCE_FOUND_BUT_WITHHELD = "EVIDENCE_FOUND_BUT_WITHHELD"
PENDING = "PENDING"

END_STATES = (RESULT, NO_EVIDENCE, RESEARCH_INCOMPLETE,
              EVENT_OUTSIDE_MEASURABLE_RANGE, EVIDENCE_FOUND_BUT_WITHHELD)

# Wording is part of the specification, not decoration. NO_EVIDENCE says this
# search found nothing; RESEARCH_INCOMPLETE says we could not look. The two are
# never displayed the same way.
STATE_LABEL = {
    RESULT: "Result",
    NO_EVIDENCE: "No qualifying evidence found in the sources searched",
    RESEARCH_INCOMPLETE: "Research could not be completed",
    EVENT_OUTSIDE_MEASURABLE_RANGE: "Event outside measurable range",
    EVIDENCE_FOUND_BUT_WITHHELD: "Finding withheld by presentation review",
    PENDING: "Awaiting evidence",
}

# ---------------------------------------------------------------------------
# The explorer prompt.
#
# Verified 2026-10-08 against the live model. Do not edit without re-testing.
#
# The CRITICAL paragraph must not be removed. Without it the model returns
# current conditions ("Brooklyn housing inventory 2025") instead of dated past
# events, and an event with no date cannot be measured, so the whole pipeline
# downstream of it has nothing to work with.
#
# The "Black clothing -> protest movements" example must not be removed either.
# It is what keeps distant directions alive, and the acceptance criterion fixed
# in advance (spec section 17) is that `Brooklyn protest attire black clothing
# 2020` survives any revision of this prompt.
# ---------------------------------------------------------------------------

EXPLORER_PROMPT = """You decide what to research about a question on New York City housing.

You do NOT answer the question. You do NOT predict. You decide where to look.

CRITICAL: You are searching for PAST EVENTS, not current conditions. Every
direction must be able to surface a specific, dated event that already happened
between 2017 and today - a policy decision, a rate change, a crisis, a ruling,
a disaster, a programme launch. The system measures what happened in the 12
months after each event, so an event with no date is useless.

Good: "Federal Reserve emergency rate cuts historical"
Bad: "current mortgage rate outlook" (no event, no date)

Good: "New York State eviction moratorium announcements"
Bad: "Brooklyn housing inventory 2025" (a condition, not an event)

For each direction, give:
- keyword: a short search phrase likely to surface dated historical events
- path: the chain of reasoning that led you there, as terms joined by arrows

A path may be distant. "Black clothing -> protest movements -> market
instability" is valid if you believe it is worth searching. Do not filter out
unusual directions.

Decide how many directions the question warrants. Do not pad.

Output ONLY valid JSON, no other text:
{"directions":[{"keyword":"...","path":"... -> ... -> ..."}]}"""

MAX_QUESTION_CHARS = 500
MAX_DIRECTIONS = 12  # a ceiling against a runaway response, not a selection rule

# ---------------------------------------------------------------------------
# Transport
# ---------------------------------------------------------------------------


class Unavailable(Exception):
    """The model could not be reached, or returned nothing usable.

    Every path that raises this ends as RESEARCH_INCOMPLETE. None of them ever
    ends as NO_EVIDENCE: not reaching the model is not evidence about the world.
    """


def api_key():
    return os.environ.get("NEBIUS_API_KEY", "").strip()


def chat(model, system, user, max_tokens=MAX_TOKENS):
    """One completion. Returns the assistant's text, or raises Unavailable."""
    key = api_key()
    if not key:
        raise Unavailable("NEBIUS_API_KEY is not set in this environment.")

    body = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        BASE_URL + "/chat/completions",
        data=body,
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
        # 401/403 is a bad key, 429 is a rate limit or an exhausted balance.
        # All of them mean we could not look, never that nothing happened.
        raise Unavailable("The model endpoint returned HTTP %s. %s"
                          % (exc.code, detail.strip()))
    except urllib.error.URLError as exc:
        raise Unavailable("The model endpoint could not be reached (%s)."
                          % exc.reason)
    except Exception as exc:
        raise Unavailable("The model endpoint failed (%s: %s)."
                          % (type(exc).__name__, exc))

    try:
        text = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise Unavailable("The model returned a response in an unexpected shape.")

    if not text or not text.strip():
        # A reasoning model that spends its whole allowance thinking returns an
        # empty content field. That is a failed call, not an empty finding.
        raise Unavailable("The model returned an empty response.")

    return text


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def extract_json(text):
    """The verified responses are bare JSON. This tolerates a wrapper anyway."""
    text = text.strip()
    try:
        return json.loads(text)
    except ValueError:
        pass

    # A fenced block, or reasoning text around the object.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except ValueError:
            pass
    raise Unavailable("The model's response was not valid JSON.")


def clean(value, limit):
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())[:limit]


def parse_directions(payload):
    raw = payload.get("directions") if isinstance(payload, dict) else None
    if not isinstance(raw, list):
        raise Unavailable("The model's response contained no directions.")

    out = []
    for item in raw[:MAX_DIRECTIONS]:
        if not isinstance(item, dict):
            continue
        keyword = clean(item.get("keyword"), 160)
        path = clean(item.get("path"), 300)
        if not keyword:
            continue
        out.append({"keyword": keyword, "path": path, "state": PENDING})

    if not out:
        raise Unavailable("The model returned directions in an unreadable form.")
    return out


# ---------------------------------------------------------------------------
# The step itself
# ---------------------------------------------------------------------------


def explore(question):
    """Question in, research directions out.

    Returns a dict the interface can render directly:

        {"ok": True,  "question": ..., "directions": [...], "model": ...}
        {"ok": False, "question": ..., "state": RESEARCH_INCOMPLETE,
         "reason": ..., "model": ...}

    The failure branch is RESEARCH_INCOMPLETE and nothing else. There is no
    path through this function that reports an empty research result, because
    the explorer has not searched anything yet - it has only decided where to
    look. Reporting "no evidence found" here would be a statement about the
    historical record made on the strength of our own failure.
    """
    question = clean(question, MAX_QUESTION_CHARS)
    base = {"question": question, "model": EXPLORER_MODEL}

    if not question:
        return dict(base, ok=False, state=RESEARCH_INCOMPLETE,
                    reason="No question was submitted.")

    try:
        text = chat(EXPLORER_MODEL, EXPLORER_PROMPT, question)
        directions = parse_directions(extract_json(text))
    except Unavailable as exc:
        return dict(base, ok=False, state=RESEARCH_INCOMPLETE, reason=str(exc))

    return dict(base, ok=True, directions=directions)


# ---------------------------------------------------------------------------
# Roll-up - spec section 10, amendment A2.
#
# States do not stay local to the direction they belong to. One incomplete
# direction makes the analysis incomplete, and that is said once at the top.
# ---------------------------------------------------------------------------


def rollup(directions):
    states = [d.get("state") for d in directions]
    if RESEARCH_INCOMPLETE in states:
        return RESEARCH_INCOMPLETE
    if PENDING in states:
        return PENDING
    if RESULT in states:
        return RESULT
    return NO_EVIDENCE
