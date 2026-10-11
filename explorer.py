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
# Based on the prompt verified 2026-10-08, with the relevance paragraph added
# on 2026-10-11 after a live run left the subject entirely. That addition has
# not been through the same testing - re-verify before the entry.
#
# What went wrong. The question was "why does autumn, the third quarter, sell
# best", typed by someone looking at a chart of Brooklyn house prices. All
# five directions came back about retail: UK retail sales, earnings calls,
# back-to-school shopping, Amazon Prime Day. The pipeline then measured
# Brooklyn house prices around Prime Day 2022 and presented it with a source,
# a date basis and two medians.
#
# "Sells best" is ambiguous on its own, and on its own was all the model got.
# The region, the market and the data window were known to the system and
# passed to nothing - the same shape of mistake as the extractor. A step
# cannot obey a constraint it was never told about. The context now goes in
# with the question, and the paragraph below requires a direction to arrive at
# housing in the named region.
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

FIRST, name the concepts the question is really about. These are the keywords.
Keep each one SHORT - one or two words, the way a person would say it out
loud, not a search phrase. "interest rates", "umbrellas", "school districts".
Decide how many the question warrants. Do not pad.

The keywords are then FIXED, and they are the whole of what you may work from.
Every direction you set out must start from one or more of them, and may
combine two or three of them. You may travel a long way from a keyword. You
may not start anywhere else. If an idea occurs to you while working that is
not among the keywords, you cannot use it.

CRITICAL: You are searching for PAST EVENTS, not current conditions. Every
direction must be able to surface a specific, dated event that already happened
between 2017 and today - a policy decision, a rate change, a crisis, a ruling,
a disaster, a programme launch. The system measures what happened in the 12
months after each event, so an event with no date is useless.

A keyword has no date. An event does. The path is how you get from one to the
other: "umbrellas" has no date, but a particular storm that flooded the city
does. Travel until you reach something that happened on a day. If a keyword
cannot be walked to any dated event, leave it out of the directions - it
stays in the keyword list, and that is an honest record of where you looked.

Good: "Federal Reserve emergency rate cuts historical"
Bad: "current mortgage rate outlook" (no event, no date)

Good: "New York State eviction moratorium announcements"
Bad: "Brooklyn housing inventory 2025" (a condition, not an event)

Every direction must end in an event that plausibly bears on residential
property prices in the region given with the question. A question can start
anywhere - the weather, what people wear, a war - but the direction you set
out from it has to arrive at housing in that region. If a direction would only
surface events in another market, another industry or another city, do not
give it.

For each direction, give:
- from: which of your keywords it starts from, one or more, copied exactly
- path: the route from those keywords to the event, as terms joined by arrows
- query: the search phrase you want run, which may be long and specific

A path may be distant. From the keyword "black clothing", the path
"Black clothing -> protest movements -> market instability" is valid if you
believe it is worth searching. Do not filter out unusual directions.

If the question is about something that recurs rather than something that
happened - a season, a yearly pattern, a busy period - say so in "recurring"
and still give what directions you can. Individual dated events inside those
seasons can be measured; the cycle itself cannot.

Output ONLY valid JSON, no other text:
{"keywords":["...","..."],
 "recurring":false,
 "directions":[{"from":["..."],"path":"... -> ... -> ...","query":"..."}]}"""

MAX_QUESTION_CHARS = 500
# Ceilings against a runaway response, not selection rules. The model decides
# how many keywords and directions a question warrants; these only stop a
# malformed reply from costing a hundred searches.
MAX_DIRECTIONS = 12
MAX_KEYWORDS = 10

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


def parse_plan(payload):
    """The keyword set, and the directions that start from it.

    The lock is checked here, not merely asked for in the prompt. A direction
    that starts from something outside the keyword list is dropped, because
    that is the one failure the lock exists to prevent: seeing A and setting
    off after B. A rule enforced only by instruction is a rule the next model
    gets to reinterpret.
    """
    if not isinstance(payload, dict):
        raise Unavailable("The model's response was not an object.")

    keywords = []
    seen = set()
    for k in (payload.get("keywords") or [])[:MAX_KEYWORDS]:
        k = clean(k, 60)
        if k and k.casefold() not in seen:
            seen.add(k.casefold())
            keywords.append(k)
    if not keywords:
        raise Unavailable("The model named no keywords for the question.")

    index = {k.casefold(): k for k in keywords}

    raw = payload.get("directions")
    if not isinstance(raw, list):
        raise Unavailable("The model's response contained no directions.")

    out = []
    outside = 0
    for item in raw[:MAX_DIRECTIONS]:
        if not isinstance(item, dict):
            continue
        query = clean(item.get("query"), 200)
        path = clean(item.get("path"), 400)
        if not query:
            continue

        origins = item.get("from")
        if isinstance(origins, str):
            origins = [origins]
        kept = []
        strayed = False
        for o in (origins or [])[:MAX_KEYWORDS]:
            o = clean(o, 60)
            if not o:
                continue
            if o.casefold() in index:
                kept.append(index[o.casefold()])
            else:
                strayed = True
        if not kept or strayed:
            # Started somewhere it never declared, so it is not inside the
            # question it set itself (spec section 8).
            outside += 1
            continue

        out.append({"from": kept, "path": path, "query": query,
                    "state": PENDING})

    if not out:
        raise Unavailable("No research direction started from the keywords the "
                          "model named, so nothing could be searched inside "
                          "the question it set itself.")

    return {
        "keywords": keywords,
        "directions": out,
        "dropped_outside_keywords": outside,
        "recurring": bool(payload.get("recurring")),
    }


# ---------------------------------------------------------------------------
# The step itself
# ---------------------------------------------------------------------------


def ask_block(question, region, data_from, data_to):
    """What the explorer is given: the question, and what it is a question about.

    The question alone is not enough. "Why does autumn sell best" is about
    retail to anyone who has not been told otherwise, and the person asking it
    was looking at a chart of house prices at the time.
    """
    lines = []
    if region:
        lines.append("REGION: %s, New York City" % region)
    lines.append("MARKET: residential property sales")
    if data_from and data_to:
        lines.append("MEASURABLE PERIOD: %s to %s" % (data_from, data_to))
    lines.append("")
    lines.append("QUESTION: " + question)
    return "\n".join(lines)


def explore(question, region="", data_from="", data_to=""):
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
        text = chat(EXPLORER_MODEL, EXPLORER_PROMPT,
                    ask_block(question, region, data_from, data_to))
        plan = parse_plan(extract_json(text))
    except Unavailable as exc:
        return dict(base, ok=False, state=RESEARCH_INCOMPLETE, reason=str(exc))

    return dict(base, ok=True, **plan)


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
