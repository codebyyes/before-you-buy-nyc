# evidence.py - the search layer and the dated-event check.
#
# This module finds events. It does not measure them: no price, median or
# percentage is computed here, and no model is ever shown a price. The
# measurement happens in main.py, from official data, after a date has been
# confirmed against a source (spec section 13).
#
# Spec sections: 10 (the five states), 11 (authoritative sources only),
# 14 (the event date must be confirmable from the source).
#
# Like explorer.py this talks to both services over the standard library. A
# search client is one POST, and a dependency whose major version can move
# under a redeploy during judging is not worth the two lines it saves.

import json
import os
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from explorer import (NO_EVIDENCE, RESEARCH_INCOMPLETE, Unavailable, chat,
                      clean, extract_json)
from explorer import EXPLORER_MODEL

TAVILY_URL = "https://api.tavily.com/search"
TIMEOUT = 60

# Section 11. Default Tavily quality was poor enough to return betting sites
# and crypto news for a housing question, and for the wrong event at that.
# The domain list and the advanced depth are both required, not tuning.
TRUSTED = [
    # Federal
    "federalreserve.gov",
    "census.gov",
    "bls.gov",
    "hud.gov",
    "federalregister.gov",
    "gao.gov",
    # New York State and City
    "ny.gov",
    "nyc.gov",
    "hcr.ny.gov",
    "comptroller.nyc.gov",
    "council.nyc.gov",
    "dos.ny.gov",
    "esd.ny.gov",
    # Press of record
    "reuters.com",
    "apnews.com",
    "nytimes.com",
    "wsj.com",
    "bloomberg.com",
    # New York business and local press, which cover the city's own decisions
    # in more detail than the national wires do
    "crainsnewyork.com",
    "thecity.nyc",
    "gothamist.com",
]

# Ten rather than five. Credits are charged per search, not per result, so the
# extra five sources are free and the page carrying the dated sentence is
# often not in the first five.
#
# An advanced search costs TWO credits, measured cleanly on the account: 47 to
# 55 across one question of four searches. An earlier estimate of one came
# from dividing a rough total by a half-remembered history and was wrong in
# the direction that flattered the budget.
MAX_RESULTS = 10
SEARCH_DEPTH = "advanced"   # basic is 1 credit and returned betting
                            # sites and crypto news; not an option
CREDITS_PER_SEARCH = 2

# One search per direction, so a question costs twice as many credits as the
# explorer produced directions: a ten-record question is twenty credits.
# Concurrency is for latency only and changes no total.
WORKERS = 8

# Based on the prompt verified 2026-10-08, with two rules added on 2026-10-11
# after it returned a wrong finding against live data. This version has not yet
# been through the same testing as the original - re-verify before the entry.
#
# What went wrong. The keyword was "Brooklyn downtown luxury condo oversupply
# 2021-2022". The search returned an Attorney General filing, and the model
# reported an event dated 2008-08-01 whose basis was the words
# "as-of-august-1-2010" inside a PDF filename. Wrong decade, wrong borough,
# and not an event at all - the as-of date of a document.
#
# The cause was structural, not a lapse: the keyword was never passed in, so
# the model was asked to find a date, with nothing to say which date mattered.
# Any document has dates in it. Section 8 says the explorer may only look for
# answers inside the question it set; the reader of the sources has to be told
# what that question was, or the constraint only exists on paper.
#
# "Do not guess. Do not use your own knowledge." is the other half: the model
# is reading sources here, not recalling. Finding nothing is a real result.
DATE_PROMPT = """From the sources below, identify ONE specific dated event that
the SEARCH TERM was looking for.

Rules:
- The event must be what the search term was looking for. If the sources are
  about a different subject, a different place, or a different period than the
  search term asked for, return {"found": false}.
- It must be an event: something that happened on a day. A decision, a vote, a
  ruling, an announcement, a rate change, a filing, a disaster, a launch.
- A document's own date is not an event. The date a report was published, the
  "as of" date of an assessment, the vintage of a dataset, a date that appears
  only in a filename - none of these are events. If that is all the sources
  offer, return {"found": false}.
- The date must be stated or clearly derivable from the source text or URL.
- If no date can be confirmed, return {"found": false}.
- Do not guess. Do not use your own knowledge.

Returning {"found": false} is a correct and useful answer. A direction that was
searched and yielded nothing is recorded as exactly that. Never stretch a
source to fit the search term.

Output ONLY valid JSON:
{"found": true, "event": "...", "date": "YYYY-MM-DD", "date_basis": "...",
 "source_url": "...", "source_type": "Government|News|Academic|Research|Public dataset"}"""

SOURCE_TYPES = ("Government", "News", "Academic", "Research", "Public dataset")


def api_key():
    return os.environ.get("TAVILY_API_KEY", "").strip()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def search(keyword):
    """Authoritative-domain results for one keyword, or raise Unavailable.

    Costs one Tavily credit. A failure here is RESEARCH_INCOMPLETE and never
    NO_EVIDENCE: an exhausted quota is a fact about us, not about the record.
    """
    key = api_key()
    if not key:
        raise Unavailable("TAVILY_API_KEY is not set in this environment.")

    payload = {
        "query": keyword,
        "max_results": MAX_RESULTS,
        "search_depth": SEARCH_DEPTH,
        "include_domains": TRUSTED,
        # Sent in the body as well as the header: both forms have been
        # accepted, and this call cannot be rehearsed against the live service
        # from the build environment.
        "api_key": key,
    }

    req = urllib.request.Request(
        TAVILY_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "replace")[:200]
        except Exception:
            pass
        # 432 and 433 are Tavily's own "plan limit reached" codes; 401 is a bad
        # key; 429 is rate limiting. Each one means the search did not happen.
        raise Unavailable("The search service returned HTTP %s. %s"
                          % (exc.code, detail.strip()))
    except urllib.error.URLError as exc:
        raise Unavailable("The search service could not be reached (%s)."
                          % exc.reason)
    except Exception as exc:
        raise Unavailable("The search service failed (%s: %s)."
                          % (type(exc).__name__, exc))

    results = body.get("results")
    if not isinstance(results, list):
        raise Unavailable("The search service returned an unexpected response.")

    hits = []
    for r in results:
        if not isinstance(r, dict):
            continue
        url = clean(r.get("url"), 400)
        if not url:
            continue
        hits.append(
            {
                "title": clean(r.get("title"), 200),
                "url": url,
                "content": clean(r.get("content"), 1200),
            }
        )
    return hits


# ---------------------------------------------------------------------------
# Dating the event
# ---------------------------------------------------------------------------


def sources_block(keyword, hits):
    parts = ["SEARCH TERM: " + keyword, ""]
    for i, h in enumerate(hits, 1):
        parts.append("[%d] %s\nURL: %s\n%s" % (i, h["title"], h["url"], h["content"]))
    return "\n".join(parts[:2]) + "\n" + "\n\n".join(parts[2:])


def valid_date(text):
    """YYYY-MM-DD and nothing else. A malformed date is no date."""
    text = (text or "").strip()[:10]
    if len(text) != 10 or text[4] != "-" or text[7] != "-":
        return None
    y, m, d = text[:4], text[5:7], text[8:10]
    if not (y.isdigit() and m.isdigit() and d.isdigit()):
        return None
    try:
        from datetime import date as _date
        return _date(int(y), int(m), int(d))
    except ValueError:
        return None


def extract_event(keyword, hits):
    """One dated event matching the keyword, or None if none can be confirmed.

    The keyword goes in with the sources. Without it the model is asked to
    find a date rather than the right date, and every document has dates in
    it - which is how a filename reading "as-of-august-1-2010" was once
    reported as an event.

    None means one thing only: the search completed and the model, having
    read the sources, reported that they held no datable event the keyword
    was looking for. That is a real result, kept as NO_EVIDENCE.

    Raising means the research could not be completed. That covers not
    reaching the service at all, and it also covers reaching it and getting
    back an answer this step cannot use - an unreadable reply, an event
    without its date or source, a source address that is not one of the
    pages the search returned. In each of those the sources may well have
    held something; we simply never learned what. Calling that an empty
    record would be reporting our own step as a fact about history.
    """
    if not hits:
        return None

    text = chat(EXPLORER_MODEL, DATE_PROMPT, sources_block(keyword, hits))
    data = extract_json(text)

    # A reply we cannot read is not a statement about the record. Only the
    # model saying "found: false" means the sources held nothing datable;
    # everything else below is our own step coming back unusable, and that
    # ends as RESEARCH_INCOMPLETE. Reporting it as NO_EVIDENCE would put words
    # in the historical record's mouth that we never had the standing to say.
    if not isinstance(data, dict):
        raise Unavailable(
            "The extraction step returned a response that was not a result "
            "object, so the sources it read could not be judged.")

    if not data.get("found"):
        return None

    when = valid_date(data.get("date"))
    event = clean(data.get("event"), 240)
    basis = clean(data.get("date_basis"), 400)
    url = clean(data.get("source_url"), 400)
    kind = clean(data.get("source_type"), 40)

    # Section 14: the date has to be confirmable, and section 11: the finding
    # has to carry a source. Missing either one is not a finding - but it is
    # also not an empty record. The model said it found something and then
    # handed back an incomplete answer, so what the sources held is unknown.
    if not when or not event or not url:
        raise Unavailable(
            "The extraction step reported an event without its date, its "
            "description or its source address, so it could not be shown.")

    # The model may paraphrase a URL. Only a URL that actually came back from
    # the search is allowed to be displayed as the source.
    known = {h["url"] for h in hits}
    if url not in known:
        match = next((h["url"] for h in hits if url and url in h["url"]), None)
        if not match:
            match = next((h["url"] for h in hits if h["url"] in url), None)
        if not match:
            raise Unavailable(
                "The extraction step returned a source address that was not "
                "among the pages the search returned, so the event it "
                "reported could not be traced to one of them.")
        url = match

    if kind not in SOURCE_TYPES:
        kind = ""

    return {
        "event": event,
        "date": when,
        "date_basis": basis,
        "source_url": url,
        "source_type": kind,
        "source_count": len(hits),
    }


# ---------------------------------------------------------------------------
# Running every direction
# ---------------------------------------------------------------------------


def gather(directions):
    """Search and date every direction, in parallel.

    A direction is searched by its `query`, which is the phrase the explorer
    composed at the far end of its path. The keywords it set out from travel
    with it and are what the reader checks the finding against.

    Returns the same list, each entry carrying one of:

        {"event": {...}}                    a dated, sourced event
        {"state": NO_EVIDENCE}              searched, nothing datable found
        {"state": RESEARCH_INCOMPLETE,      could not look
         "reason": ...}

    Nothing here is measured and nothing here is ranked. The directions come
    back in the order the explorer gave them.
    """
    queries = [d["query"] for d in directions]
    out = [dict(d) for d in directions]

    def one(query):
        try:
            return ("hits", search(query))
        except Unavailable as exc:
            return ("error", str(exc))

    with ThreadPoolExecutor(max_workers=min(WORKERS, max(1, len(queries)))) as pool:
        searched = list(pool.map(one, queries))

    def date_one(job):
        query, (kind, value) = job
        if kind == "error":
            return ("error", value)
        try:
            return ("event", extract_event(query, value), len(value))
        except Unavailable as exc:
            return ("error", str(exc))

    with ThreadPoolExecutor(max_workers=min(WORKERS, max(1, len(queries)))) as pool:
        dated = list(pool.map(date_one, zip(queries, searched)))

    for entry, result in zip(out, dated):
        if result[0] == "error":
            entry["state"] = RESEARCH_INCOMPLETE
            entry["reason"] = result[1]
            continue
        event = result[1]
        entry["sources_searched"] = result[2]
        if event is None:
            entry["state"] = NO_EVIDENCE
        else:
            entry["event"] = event
    return out
