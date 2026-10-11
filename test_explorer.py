# test_explorer.py - offline checks on explorer.py.
#
#     python test_explorer.py
#
# No network, no API key, no spend. Run it from the project directory.
#
# Two things here are worth more than the rest. First, the prompt is checked
# literally: the CRITICAL paragraph and the distant-path example have both been
# removed by a well-meaning edit before, and removing either one breaks the
# pipeline downstream in a way that looks like a search problem. Second, every
# failure path is checked to land on RESEARCH_INCOMPLETE and to be worded as
# one, because a failure that reads as "no evidence found" is a false statement
# about the historical record and is the worst way this system can fail.

import json
import os
import sys

import explorer as ex

fails = []


def check(name, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + name + ("  " + detail if detail and not cond else ""))
    if not cond:
        fails.append(name)


print("prompt integrity")
check("CRITICAL paragraph present", "CRITICAL: You are searching for PAST EVENTS" in ex.EXPLORER_PROMPT)
check("distant-path example present", "Black clothing -> protest movements" in ex.EXPLORER_PROMPT)
check("relevance is about consequence, not the event's address",
      "What must connect to the region is the consequence" in ex.EXPLORER_PROMPT)
check("an event elsewhere is still allowed",
      "may have happened anywhere" in ex.EXPLORER_PROMPT,
      "a campus announced in Queens moves prices in Brooklyn")
check("a trend is rejected as well as a condition",
      "A trend is not an event" in ex.EXPLORER_PROMPT)
check("queries go out in English whatever the question's language",
      "WRITE EVERY QUERY IN ENGLISH" in ex.EXPLORER_PROMPT)
check("keywords and records are not paired off",
      "Never pair them off one for one" in ex.EXPLORER_PROMPT)
check("records are capped at ten", ex.MAX_DIRECTIONS == 10)
check("padding is still forbidden", "Do not pad." in ex.EXPLORER_PROMPT)
check("bare JSON instruction present", 'Output ONLY valid JSON, no other text:' in ex.EXPLORER_PROMPT)
check("no padding instruction present", "Do not pad." in ex.EXPLORER_PROMPT)
check("explorer model id lowercase", ex.EXPLORER_MODEL == "nvidia/nemotron-3-super-120b-a12b")
check("reviewer model id mixed case", ex.REVIEWER_MODEL == "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B")

print("\nparsing")
GOOD = json.dumps({
    "keywords": ["interest rates", "umbrellas", "school districts"],
    "recurring": False,
    "directions": [
        {"from": ["umbrellas"], "path": "umbrellas -> rainfall -> flooding",
         "query": "Hurricane Ida September 2021 New York City flooding"},
        {"from": ["interest rates", "school districts"],
         "path": "rates -> borrowing -> family moves",
         "query": "Federal Reserve rate decision September 2019"},
    ],
})

plan = ex.parse_plan(ex.extract_json(GOOD))
check("bare JSON parses", len(plan["directions"]) == 2)
check("keywords come back in order", plan["keywords"][0] == "interest rates")
check("every direction starts pending",
      all(d["state"] == ex.PENDING for d in plan["directions"]))
check("a direction may combine keywords", plan["directions"][1]["from"] ==
      ["interest rates", "school districts"])

check("fenced JSON parses",
      len(ex.parse_plan(ex.extract_json("```json\n" + GOOD + "\n```"))["directions"]) == 2)
check("reasoning wrapper tolerated",
      len(ex.parse_plan(ex.extract_json("<think>hmm</think>\n" + GOOD))["directions"]) == 2)

print("\nthe lock is enforced here, not only asked for in the prompt")
strayed = json.dumps({
    "keywords": ["interest rates"],
    "directions": [
        {"from": ["interest rates"], "path": "p", "query": "fed rate cut 2019"},
        {"from": ["crypto"], "path": "p", "query": "bitcoin crash 2022"},
        {"from": ["interest rates", "crypto"], "path": "p", "query": "both"},
    ],
})
plan = ex.parse_plan(ex.extract_json(strayed))
check("a direction from outside the keywords is dropped",
      len(plan["directions"]) == 1, str(plan["directions"]))
check("so is one that mixes an outside concept in",
      plan["directions"][0]["query"] == "fed rate cut 2019")
check("and the count of dropped directions is reported",
      plan["dropped_outside_keywords"] == 2)
check("keyword matching ignores case", len(ex.parse_plan(ex.extract_json(json.dumps({
    "keywords": ["Interest Rates"],
    "directions": [{"from": ["interest rates"], "path": "p", "query": "q"}],
})))["directions"]) == 1)
check("recurring is carried through", ex.parse_plan(ex.extract_json(json.dumps({
    "keywords": ["autumn"], "recurring": True,
    "directions": [{"from": ["autumn"], "path": "p", "query": "q"}],
})))["recurring"] is True)

print("\nmalformed plans are refused, never half-accepted")
for bad, why in [
    ("not json at all", "prose"),
    ('{"keywords":["a"],"directions":[]}', "no directions"),
    ('{"keywords":[],"directions":[{"from":["a"],"path":"p","query":"q"}]}', "no keywords"),
    ('{"directions":[{"from":["a"],"path":"p","query":"q"}]}', "keywords missing"),
    ('{"keywords":["a"],"directions":"nope"}', "wrong type"),
    ('{"keywords":["a"],"directions":[{"from":["a"],"path":"p"}]}', "no query"),
    ('{"keywords":["a"],"directions":[{"path":"p","query":"q"}]}', "no origin"),
]:
    try:
        ex.parse_plan(ex.extract_json(bad))
        check("rejects " + why, False)
    except ex.Unavailable:
        check("rejects " + why, True)

longer = json.dumps({"keywords": ["k" * 900],
                     "directions": [{"from": ["k" * 900], "path": "y" * 900,
                                     "query": "q" * 900}]})
plan = ex.parse_plan(ex.extract_json(longer))
check("truncates long fields",
      len(plan["keywords"][0]) == 60 and len(plan["directions"][0]["path"]) == 400
      and len(plan["directions"][0]["query"]) == 200)

many = json.dumps({"keywords": ["k"],
                   "directions": [{"from": ["k"], "path": "p", "query": "q%d" % i}
                                  for i in range(40)]})
check("caps runaway direction count",
      len(ex.parse_plan(ex.extract_json(many))["directions"]) == ex.MAX_DIRECTIONS)

print("\nfailure paths all land on RESEARCH_INCOMPLETE")
os.environ.pop("NEBIUS_API_KEY", None)
r = ex.explore("Will Brooklyn prices rise next year?")
check("missing key -> incomplete", r["ok"] is False and r["state"] == ex.RESEARCH_INCOMPLETE)
check("missing key -> names the variable", "NEBIUS_API_KEY" in r["reason"], r["reason"])

r = ex.explore("   ")
check("empty question -> incomplete", r["ok"] is False and r["state"] == ex.RESEARCH_INCOMPLETE)

os.environ["NEBIUS_API_KEY"] = "test-not-a-real-key"


def stub(text):
    def fake(model, system, user, max_tokens=ex.MAX_TOKENS):
        return text
    return fake


real_chat = ex.chat

ex.chat = stub(GOOD)
r = ex.explore("Did the mayor do a good job?")
check("happy path -> ok", r["ok"] is True and len(r["directions"]) == 2)
check("happy path -> the keyword set comes back", r["keywords"][0] == "interest rates")
check("happy path -> every direction pending",
      all(x["state"] == ex.PENDING for x in r["directions"]))

ex.chat = stub("I think prices will go up.")
r = ex.explore("anything")
check("unparseable -> incomplete", r["ok"] is False and r["state"] == ex.RESEARCH_INCOMPLETE)


def raiser(msg):
    def fake(model, system, user, max_tokens=ex.MAX_TOKENS):
        raise ex.Unavailable(msg)
    return fake


for msg in ["The model endpoint returned HTTP 429.",
            "The model endpoint returned HTTP 401.",
            "The model returned an empty response.",
            "The model endpoint could not be reached (timed out)."]:
    ex.chat = raiser(msg)
    r = ex.explore("anything")
    check("'%s' -> incomplete" % msg[:38], r["state"] == ex.RESEARCH_INCOMPLETE)

print("\nno failure path can word itself as an empty result")
banned = ["no evidence", "no qualifying", "nothing was found", "not found",
          "empty result", "no historical"]
ex.chat = raiser("The model endpoint returned HTTP 429. quota exceeded")
seen = []
for question in ["", "   ", "a real question"]:
    for stub_text in [None]:
        r = ex.explore(question)
        seen.append((r.get("reason") or "").lower())
ex.chat = stub("garbage")
seen.append((ex.explore("q").get("reason") or "").lower())
leaks = [(s, b) for s in seen for b in banned if b in s]
check("no banned wording in any reason", not leaks, repr(leaks))
check("RESEARCH_INCOMPLETE label is the specified wording",
      ex.STATE_LABEL[ex.RESEARCH_INCOMPLETE] == "Research could not be completed")
check("NO_EVIDENCE label says 'in the sources searched'",
      "sources searched" in ex.STATE_LABEL[ex.NO_EVIDENCE])

print("\nthe presentation gate")
check("five questions, not four and not six",
      all(("%d." % n) in ex.REVIEWER_PROMPT for n in range(1, 6))
      and "6." not in ex.REVIEWER_PROMPT)
check("the gate is told not to judge truth",
      "You do not check\nwhether it is true" in ex.REVIEWER_PROMPT)
check("and not to reopen whether the direction was worth taking",
      "worth taking" in ex.REVIEWER_PROMPT)
check("revisions are capped at two", ex.MAX_REVISIONS == 2)
check("the reviewer gets a reasoning model's token budget, not a verdict's",
      "max_tokens=MAX_TOKENS" in open("explorer.py").read()
      and ex.MAX_TOKENS >= 2048,
      "Nano reasons before it answers; a small budget comes back empty")
check("a revision may not fetch anything new",
      "do not search for anything" in ex.REVISE_PROMPT)

for text, want in [("PASS", (True, [])), ("pass\n", (True, [])),
                   ("FAIL 1 2 3 4", (False, [1, 2, 3, 4])),
                   ("FAIL\n2 5", (False, [2, 5])),
                   ("FAIL 2, 3", (False, [2, 3])),
                   ("FAIL", (False, [])),
                   ("FAIL 9 2 2", (False, [2]))]:
    check("verdict %r" % text, ex.parse_verdict(text) == want)
for bad in ["maybe", "", "I think it is fine"]:
    try:
        ex.parse_verdict(bad)
        check("rejects non-verdict %r" % bad, False)
    except ex.Unavailable:
        check("rejects non-verdict %r" % bad, True)

EVENT = {"event": "Gowanus rezoning approved", "date": "2021-11-23",
         "date_basis": "approved by the City Council on November 23, 2021",
         "source_url": "https://nyc.gov/x", "source_type": "Government"}
MEASURE = {"pre_median": 899000, "post_median": 960000, "change": 6.79,
           "months_after": 12, "pre_start": "2020-11-23",
           "pre_end": "2021-11-22", "post_start": "2021-11-23",
           "post_end": "2022-11-22"}

used = []


def scripted(replies):
    it = iter(replies)
    def fake(model, system, user, max_tokens=ex.MAX_TOKENS):
        used.append(model)
        return next(it)
    return fake


ex.chat = scripted(["PASS"])
ok, ev, _p, _f, n = ex.review(EVENT, "a -> b", MEASURE)
check("a clean finding passes with no revision", ok and n == 0)
check("the reviewer model is the one used", used[0] == ex.REVIEWER_MODEL)

ex.chat = scripted(["FAIL 2",
                    json.dumps({"event": "Rezoning approved", "path": "a -> b"}),
                    "PASS"])
ok, ev, _p, _f, n = ex.review(EVENT, "a -> b", MEASURE)
check("one rewrite can save a finding", ok and n == 1)
check("the rewrite changed the wording", ev["event"] != EVENT["event"])
check("the rewrite did not touch the date", ev["date"] == EVENT["date"])
check("nor the source", ev["source_url"] == EVENT["source_url"])

ex.chat = scripted(["FAIL 2 5", json.dumps({"event": "x", "path": "p"}),
                    "FAIL 2 5", json.dumps({"event": "y", "path": "p"}),
                    "FAIL 2 5"])
ok, _ev, _p, qfails, n = ex.review(EVENT, "a -> b", MEASURE)
check("two rewrites and no more", (not ok) and n == ex.MAX_REVISIONS)
check("the failing questions are reported", qfails == [2, 5])

print("\nthe gate working is not an apology")
APOLOGY = ["sorry", "unfortunately", "unable", "apolog", "regret", "fail"]
for fs in ([1], [2], [3], [4], [5], [2, 3, 5], []):
    said = ex.withheld_reason(fs).lower()
    leaked = [w for w in APOLOGY if w in said]
    check("reason for %s avoids apology wording" % (fs or "no numbers",),
          not leaked, said)
check("a withheld reason names the category",
      "causal language" in ex.withheld_reason([2]))


def unreachable(model, system, user, max_tokens=ex.MAX_TOKENS):
    raise ex.Unavailable("The model endpoint returned HTTP 429.")


ex.chat = unreachable
try:
    ex.review(EVENT, "a -> b", MEASURE)
    check("an unreachable reviewer raises rather than withholding", False)
except ex.Unavailable:
    check("an unreachable reviewer raises rather than withholding", True)

ex.chat = real_chat

print("\nroll-up")
check("one incomplete makes the analysis incomplete",
      ex.rollup([{"state": ex.RESULT}, {"state": ex.RESEARCH_INCOMPLETE}]) == ex.RESEARCH_INCOMPLETE)
check("incomplete outranks pending",
      ex.rollup([{"state": ex.PENDING}, {"state": ex.RESEARCH_INCOMPLETE}]) == ex.RESEARCH_INCOMPLETE)
check("pending while any direction is unsearched",
      ex.rollup([{"state": ex.RESULT}, {"state": ex.PENDING}]) == ex.PENDING)
check("all no-evidence rolls up to no-evidence",
      ex.rollup([{"state": ex.NO_EVIDENCE}, {"state": ex.NO_EVIDENCE}]) == ex.NO_EVIDENCE)
check("a result among no-evidence rolls up to result",
      ex.rollup([{"state": ex.NO_EVIDENCE}, {"state": ex.RESULT}]) == ex.RESULT)

ex.chat = real_chat

print("\nrequest shape (built, not sent)")
sent = {}


class FakeResp:
    def __init__(self, body):
        self.body = body
    def read(self):
        return self.body
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


def fake_urlopen(req, timeout=None):
    sent["url"] = req.full_url
    sent["method"] = req.get_method()
    sent["headers"] = {k.lower(): v for k, v in req.header_items()}
    sent["body"] = json.loads(req.data.decode("utf-8"))
    sent["timeout"] = timeout
    return FakeResp(json.dumps({"choices": [{"message": {"content": GOOD}}]}).encode())


ex.urllib.request.urlopen = fake_urlopen
r = ex.explore("Will Brooklyn prices rise next year?",
               region="Brooklyn", data_from="2017-01-01", data_to="2026-08-31")
check("call succeeds through the real transport", r["ok"] is True)
check("endpoint is the region-free token factory url",
      sent["url"] == "https://api.tokenfactory.nebius.com/v1/chat/completions", sent.get("url", ""))
check("POST", sent["method"] == "POST")
check("bearer auth header", sent["headers"].get("Authorization".lower(), "").startswith("Bearer "))
check("json content type", sent["headers"].get("content-type") == "application/json")
check("model is the explorer", sent["body"]["model"] == ex.EXPLORER_MODEL)
check("system message is the verified prompt", sent["body"]["messages"][0]["content"] == ex.EXPLORER_PROMPT)
user_msg = sent["body"]["messages"][1]["content"]
check("user message carries the question", "Will Brooklyn prices rise next year?" in user_msg)
check("user message names the region", "REGION: Brooklyn, New York City" in user_msg, user_msg)
check("user message names the market", "MARKET: residential property sales" in user_msg)
check("user message names the measurable period",
      "MEASURABLE PERIOD: 2017-01-01 to 2026-08-31" in user_msg)
check("max_tokens is generous enough for a reasoning model",
      sent["body"]["max_tokens"] >= 2048)
check("timeout set", sent["timeout"] == ex.TIMEOUT)

print()
if fails:
    print("FAILED %d check(s): %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("all checks passed")
