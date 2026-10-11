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

# ---------------------------------------------------------------------------
# The presentation gate - spec section 9, amendment A10.
#
# Why there is a second model at all: the first substantive response this
# project got from a language model was that it could not be built, because a
# model asked to research a question will talk itself into an answer. This
# gate exists against that one named failure mode, not for general safety.
#
# The explorer is still allowed to reason toward whatever it likes. What it is
# not allowed to do is be the one who decides that its reasoning has become a
# result.
#
# The five questions are fixed. Do not add a sixth and do not reword them into
# an open-ended check: an open re-check hands substantive judgement back to a
# model, which is exactly what the narrow scope prevents. In particular the
# reviewer is never asked whether the event is real or whether the direction
# was worth taking. Question 5 asks whether a sentence claims more than its
# evidence carries, not whether the underlying event is true.
#
# Questions 1 and 4 are guaranteed by construction here - the interface always
# prints a source and always prints the window. They are still asked, because
# the gate checks the presentation as a reader meets it, not as the programmer
# believes it to be.
#
# Observed behaviour, verified 2026-10-08: given a statement containing four
# deliberate violations it returned FAIL followed by "1 2 3 4". Four tokens and
# no elaboration. For a gate that is correct behaviour - do not "improve" the
# prompt because the answers look terse.
# ---------------------------------------------------------------------------

REVIEWER_PROMPT = """You check how a finding is presented. You do not check
whether it is true.

Answer these five questions about the text below:

1. Does every presented event carry an identifiable source?
2. Is causal language used where only sequence is established?
3. Does the result contain a conclusion, prediction, recommendation or
   probability?
4. Is the observation window stated?
5. Is the claim stronger than the underlying evidence?

A finding fails if 1 or 4 is answered no, or if 2, 3 or 5 is answered yes.

Do not consider whether the event really happened, whether the research
direction was worth taking, or whether the figures are interesting. Those are
not yours to judge.

Reply with one word, PASS or FAIL. If FAIL, follow it with the numbers of the
questions that failed, separated by spaces. Nothing else."""

# Revisions are capped at two. The explorer may rewrite how it said something;
# it may not go and find something else to say.
MAX_REVISIONS = 2

REVISE_PROMPT = """A presentation review rejected the text below on the
numbered grounds listed. Rewrite it so that it passes.

1. Every event must carry an identifiable source.
2. No causal language where only sequence is established. Write what followed,
   not what caused.
3. No conclusion, prediction, recommendation or probability.
4. The observation window must be stated.
5. No claim stronger than the evidence carries.

You may only use the evidence already given to you. Do not add an event, do
not change the date, do not search for anything, do not introduce a figure
that is not already here. You are changing how this is said, nothing else.

Output ONLY valid JSON, no other text:
{"event":"...","path":"... -> ... -> ..."}"""

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
# Running the gate
# ---------------------------------------------------------------------------

QUESTION_NAMES = {
    1: "an event without an identifiable source",
    2: "causal language where only sequence is established",
    3: "a conclusion, prediction, recommendation or probability",
    4: "no observation window stated",
    5: "a claim stronger than the evidence",
}


def parse_verdict(text):
    """PASS, or FAIL and which questions. Anything else is not a verdict."""
    head = (text or "").strip()
    upper = head.upper()
    if upper.startswith("PASS"):
        return True, []
    if not upper.startswith("FAIL"):
        raise Unavailable("The reviewer did not answer PASS or FAIL.")
    numbers = []
    for token in upper[4:].replace(",", " ").split():
        if token.isdigit() and 1 <= int(token) <= 5 and int(token) not in numbers:
            numbers.append(int(token))
    # A FAIL with no numbers is still a FAIL. The gate is not asked to justify
    # itself, and a verdict without a reason is not a reason to let it through.
    return False, numbers


def finding_text(event, path, measure):
    """The finding as the reader meets it, which is what the gate judges."""
    lines = [
        "EVENT: %s" % event.get("event", ""),
        "DATE: %s" % event.get("date", ""),
        "DATE BASIS: %s" % event.get("date_basis", ""),
        "SOURCE: %s (%s)" % (event.get("source_url", ""),
                             event.get("source_type", "unstated")),
        "RESEARCH PATH: %s" % path,
    ]
    if measure:
        lines.append(
            "MEASURED: median sale price %s in the %s months before the event "
            "date and %s in the %s after it, a change of %s. Window before: "
            "%s to %s. Window after: %s to %s."
            % (measure.get("pre_median"), 12, measure.get("post_median"),
               ("%s" % measure.get("months_after")),
               ("%s%%" % measure.get("change")),
               measure.get("pre_start"), measure.get("pre_end"),
               measure.get("post_start"), measure.get("post_end")))
    return "\n".join(lines)


def review(event, path, measure):
    """Run the gate, revising at most twice.

    Returns (passed, event, path, failures, revisions).

    A finding that still fails is withheld, which is the gate working. A
    reviewer that cannot be reached is a different thing entirely and raises,
    so the caller can record it as research that did not complete rather than
    as a finding that was blocked.
    """
    failures = []
    for attempt in range(MAX_REVISIONS + 1):
        verdict = chat(REVIEWER_MODEL, REVIEWER_PROMPT,
                       finding_text(event, path, measure), max_tokens=256)
        passed, failures = parse_verdict(verdict)
        if passed:
            return True, event, path, [], attempt
        if attempt == MAX_REVISIONS:
            break

        grounds = ", ".join(str(n) for n in failures) or "unspecified"
        revised = chat(
            EXPLORER_MODEL,
            REVISE_PROMPT,
            "REJECTED ON: %s\n\n%s" % (grounds, finding_text(event, path, measure)),
        )
        try:
            data = extract_json(revised)
        except Unavailable:
            break
        if not isinstance(data, dict):
            break
        new_event = clean(data.get("event"), 240)
        new_path = clean(data.get("path"), 400)
        if not new_event:
            break
        # Only the wording changes. The date, the source and every figure stay
        # exactly as the evidence and the program produced them.
        event = dict(event, event=new_event)
        path = new_path or path

    return False, event, path, failures, MAX_REVISIONS


def withheld_reason(failures):
    """What was wrong, without reproducing what was blocked.

    The count and the category are shown; the text is not. Publishing output
    that failed the gate would be a way around the gate.
    """
    named = [QUESTION_NAMES[n] for n in failures if n in QUESTION_NAMES]
    if not named:
        return ("Presentation review did not pass it within the permitted "
                "revisions.")
    if len(named) == 1:
        return "Presentation review found " + named[0] + "."
    return ("Presentation review found " + ", ".join(named[:-1]) + " and "
            + named[-1] + ".")


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
