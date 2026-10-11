# Local harness for the whole two-step flow, with every outside service
# stubbed. No Nebius call, no Tavily credit, no NYC Open Data request.
#
# EVERY PRICE IN THIS HARNESS IS SYNTHETIC. It exists to exercise layout and
# the state machine. Nothing here ships and nothing here is a measurement.
#
#     python tools/serve_local.py
#
# Kept in the repo on purpose: it used to live in a session scratchpad, which
# disappears when the frame changes, and docs/NEXT.md tells the next session to
# verify the two modified prompts with it. It is NOT part of what 802 pulls
# into Replit - the one-line pull command does not copy it and should not.

import json
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

import evidence
import explorer
import main

PORT = 8746

# --- step one -------------------------------------------------------------

DIRECTIONS = [
    ("Brooklyn Gowanus rezoning 2021 vote outcome housing supply",
     "rezoning -> permitted density -> new supply -> price pressure"),
    ("Federal Reserve emergency rate cuts historical",
     "mortgage rates -> borrowing cost -> buyer demand -> prices"),
    ("Lehman Brothers collapse September 2008 housing",
     "credit crisis -> lending freeze -> transaction volume -> prices"),
    ("New York State eviction moratorium announcements",
     "tenant protection -> landlord returns -> small-building sales"),
    ("Brooklyn protest attire black clothing 2020",
     "black clothing -> protest movements -> market instability"),
    ("Brooklyn tenant displacement rezoning 2019 turnover",
     "rezoning -> displacement -> tenant turnover"),
]

EXPLORE_JSON = json.dumps({
    "keywords": ["rezoning", "interest rates", "storms", "evictions",
                 "black clothing"],
    "recurring": False,
    "directions": [
        {"from": ["rezoning"],
         "path": "rezoning -> permitted density -> new supply -> price pressure",
         "query": DIRECTIONS[0][0]},
        {"from": ["interest rates"],
         "path": "interest rates -> borrowing cost -> buyer demand",
         "query": DIRECTIONS[1][0]},
        {"from": ["storms", "interest rates"],
         "path": "storms -> flood risk -> insurance cost -> credit terms",
         "query": DIRECTIONS[2][0]},
        {"from": ["evictions"],
         "path": "evictions -> tenant protection -> landlord returns",
         "query": DIRECTIONS[3][0]},
        {"from": ["black clothing"],
         "path": "Black clothing -> protest movements -> market instability",
         "query": DIRECTIONS[4][0]},
        {"from": ["rezoning", "evictions"],
         "path": "rezoning -> displacement -> tenant turnover",
         "query": DIRECTIONS[5][0]},
    ],
})

# --- step two: one of each state ------------------------------------------

EVENTS = {
    DIRECTIONS[0][0]: {
        "found": True,
        "event": "Gowanus Neighborhood Rezoning approved by the New York City Council",
        "date": "2021-11-23",
        "date_basis": "The Gowanus Neighborhood Rezoning was subsequently "
                      "approved by the City Council on November 23, 2021.",
        "source_url": "https://www.nyc.gov/site/planning/plans/gowanus/gowanus.page",
        "source_type": "Government",
    },
    # Recent enough that the window after it is short - exercises the
    # incomplete-window wording.
    DIRECTIONS[1][0]: {
        "found": True,
        "event": "Federal Reserve lowers the target range for the federal funds rate",
        "date": "2026-03-18",
        "date_basis": "Implementation Note issued March 18, 2026.",
        "source_url": "https://www.federalreserve.gov/newsevents/pressreleases/"
                      "monetary20260318a.htm",
        "source_type": "Government",
    },
    # Real, dated, sourced - and before anything this data can measure.
    DIRECTIONS[2][0]: {
        "found": True,
        "event": "Lehman Brothers files for Chapter 11 bankruptcy protection",
        "date": "2008-09-15",
        "date_basis": "Filed for Chapter 11 bankruptcy protection on "
                      "September 15, 2008.",
        "source_url": "https://www.reuters.com/article/lehman-bankruptcy",
        "source_type": "News",
    },
    # Searched, nothing datable - a real research result.
    DIRECTIONS[3][0]: {"found": False},
    # Found, dated, sourced - and worded as a causal claim, so the gate stops
    # it. This is the gate working, not a failure.
    DIRECTIONS[5][0]: {
        "found": True,
        "event": "Rezoning caused widespread tenant displacement across "
                 "Brooklyn, which drove prices up",
        "date": "2019-06-14",
        "date_basis": "Effective June 14, 2019.",
        "source_url": "https://hcr.ny.gov/example",
        "source_type": "Government",
    },
}

HITS = {
    "https://hcr.ny.gov/example": "NYS Homes and Community Renewal",
    "https://www.nyc.gov/site/planning/plans/gowanus/gowanus.page": "NYC Planning",
    "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260318a.htm":
        "Federal Reserve",
    "https://www.reuters.com/article/lehman-bankruptcy": "Reuters",
}


def fake_search(keyword):
    # The last direction fails at the search step: RESEARCH_INCOMPLETE.
    if keyword == DIRECTIONS[4][0]:
        raise explorer.Unavailable(
            'The search service returned HTTP 432. {"detail":"plan limit reached"}')
    ev = EVENTS.get(keyword) or {}
    url = ev.get("source_url") or "https://www.nyc.gov/example"
    return [{"title": HITS.get(url, "Source"), "url": url,
             "content": ev.get("date_basis", "No date is stated here.")}
            for _ in range(5)]


def fake_chat(model, system, user, max_tokens=explorer.MAX_TOKENS):
    if system == explorer.REVIEWER_PROMPT:
        if "Gowanus" in user:
            return ""   # an empty verdict, exactly what the live run hit
        # Everything passes except the deliberately causal one, which keeps
        # failing so the withheld state can be seen.
        return "FAIL 2 5" if "caused widespread" in user or "drove" in user \
               else "PASS"
    if system == explorer.REVISE_PROMPT:
        # A rewrite that does not fix the problem, so the gate holds.
        return json.dumps({"event": "Rezoning caused displacement which drove "
                                    "prices up", "path": "a -> b"})
    if system == explorer.EXPLORER_PROMPT:
        assert "REGION:" in user and "QUESTION:" in user, \
            "explorer did not receive its context"
        return EXPLORE_JSON
    assert system == evidence.DATE_PROMPT, "unexpected prompt"
    assert "SEARCH TERM:" in user, "keyword was not passed to the extractor"
    for keyword, ev in EVENTS.items():
        if (ev.get("date_basis") or "\x00") in user:
            return json.dumps(ev)
    return json.dumps({"found": False})


explorer.chat = fake_chat
evidence.search = fake_search
evidence.chat = fake_chat

# --- synthetic official data ----------------------------------------------

COVERAGE = {
    "annual_min": date(2016, 1, 1), "annual_max": date(2025, 12, 31),
    "annual_n": 845607, "rolling_min": date(2025, 9, 1),
    "rolling_max": date(2026, 8, 31), "rolling_n": 82345,
    "latest": date(2026, 8, 31),
    "annual_updated": date(2026, 6, 9), "rolling_updated": date(2026, 9, 15),
}

rng = random.Random(802)
SALES = []
_d = date(2016, 1, 1)
while _d <= COVERAGE["latest"]:
    drift = 850000 + (_d - date(2016, 1, 1)).days * 55
    for _ in range(9):
        SALES.append((_d, int(rng.gauss(drift, 260000)) + 100000,
                      main.RESIDENTIAL[rng.randrange(9)]))
    _d += timedelta(days=1)
SALES = [(d, p, c) for (d, p, c) in SALES if p >= main.MIN_PRICE]

main.coverage_info = lambda: dict(COVERAGE)
main.fetch_span = lambda coverage, borough, start, end: []
main.parse_rows = lambda rows: list(SALES)


def fake_context(borough, borough_name):
    cur_end = COVERAGE["latest"] + timedelta(days=1)
    cur_start = main.add_months(cur_end, -12)
    prior_start = main.add_months(cur_start, -12)
    quarters = main.quarters_ending(COVERAGE["latest"])
    classes = []
    for c in main.RESIDENTIAL:
        cur = [p for (d, p, k) in SALES if k == c and cur_start <= d < cur_end]
        pri = [p for (d, p, k) in SALES if k == c and prior_start <= d < cur_start]
        m, n = main.median_of(cur)
        pm, pn = main.median_of(pri)
        classes.append({"category": c, "median": m, "count": n,
                        "prior_median": pm, "prior_count": pn,
                        "change": main.pct_change(pm, m),
                        "count_change": n - pn})
    am, an = main.median_of(main.window(SALES, cur_start, cur_end))
    pm, pn = main.median_of(main.window(SALES, prior_start, cur_start))
    trend = []
    for qs, qe in quarters:
        m, n = main.median_of(main.window(SALES, qs, qe))
        trend.append({"label": "%d Q%d" % (qs.year, (qs.month - 1) // 3 + 1),
                      "median": m, "count": n, "partial": qe > cur_end,
                      "through": COVERAGE["latest"] if qe > cur_end
                                 else qe - timedelta(days=1)})
    return {
        "borough": borough_name, "borough_code": borough, "coverage": dict(COVERAGE),
        "cur_start": cur_start, "cur_end": cur_end - timedelta(days=1),
        "prior_start": prior_start, "prior_end": cur_start - timedelta(days=1),
        "classes": classes, "all_median": am, "all_count": an,
        "all_prior_median": pm, "all_prior_count": pn,
        "all_change": main.pct_change(pm, am),
        "all_count_change": an - pn, "trend": trend,
        "span_start": quarters[0][0],
        "measurable_from": main.earliest_measurable(COVERAGE),
        "rows_examined": len(SALES),
        "annual_label": main.ANNUAL, "rolling_label": main.ROLLING,
        "min_price": main.MIN_PRICE, "class_count": len(main.RESIDENTIAL),
        "trend_quarters": len(trend), "trend_years": round(len(trend) / 4),
    }


main.build_context = fake_context

print("SYNTHETIC DATA. %s rows generated. Nothing here is a measurement."
      % format(len(SALES), ","))
main.app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True)
