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
check("bare JSON instruction present", 'Output ONLY valid JSON, no other text:' in ex.EXPLORER_PROMPT)
check("no padding instruction present", "Do not pad." in ex.EXPLORER_PROMPT)
check("explorer model id lowercase", ex.EXPLORER_MODEL == "nvidia/nemotron-3-super-120b-a12b")
check("reviewer model id mixed case", ex.REVIEWER_MODEL == "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B")

print("\nparsing")
good = '{"directions":[{"keyword":"Federal Reserve emergency rate cuts historical","path":"rates -> mortgages -> prices"}]}'
d = ex.parse_directions(ex.extract_json(good))
check("bare JSON parses", len(d) == 1 and d[0]["state"] == ex.PENDING)

fenced = "```json\n" + good + "\n```"
check("fenced JSON parses", len(ex.parse_directions(ex.extract_json(fenced))) == 1)

thought = "<think>I should consider rates.</think>\n" + good
check("reasoning wrapper tolerated", len(ex.parse_directions(ex.extract_json(thought))) == 1)

for bad, why in [
    ("not json at all", "prose"),
    ('{"directions":[]}', "empty list"),
    ('{"directions":"nope"}', "wrong type"),
    ('{"other":1}', "missing key"),
    ('{"directions":[{"path":"a -> b"}]}', "no keyword"),
]:
    try:
        ex.parse_directions(ex.extract_json(bad))
        check("rejects " + why, False)
    except ex.Unavailable:
        check("rejects " + why, True)

long_kw = json.dumps({"directions": [{"keyword": "x" * 900, "path": "y" * 900}]})
d = ex.parse_directions(ex.extract_json(long_kw))
check("truncates long fields", len(d[0]["keyword"]) == 160 and len(d[0]["path"]) == 300)

many = json.dumps({"directions": [{"keyword": "k%d" % i, "path": "p"} for i in range(40)]})
check("caps runaway direction count",
      len(ex.parse_directions(ex.extract_json(many))) == ex.MAX_DIRECTIONS)

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

ex.chat = stub(good)
r = ex.explore("Did the mayor do a good job?")
check("happy path -> ok", r["ok"] is True and len(r["directions"]) == 1)
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
    return FakeResp(json.dumps({"choices": [{"message": {"content": good}}]}).encode())


ex.urllib.request.urlopen = fake_urlopen
r = ex.explore("Will Brooklyn prices rise next year?")
check("call succeeds through the real transport", r["ok"] is True)
check("endpoint is the region-free token factory url",
      sent["url"] == "https://api.tokenfactory.nebius.com/v1/chat/completions", sent.get("url", ""))
check("POST", sent["method"] == "POST")
check("bearer auth header", sent["headers"].get("Authorization".lower(), "").startswith("Bearer "))
check("json content type", sent["headers"].get("content-type") == "application/json")
check("model is the explorer", sent["body"]["model"] == ex.EXPLORER_MODEL)
check("system message is the verified prompt", sent["body"]["messages"][0]["content"] == ex.EXPLORER_PROMPT)
check("user message is the question alone",
      sent["body"]["messages"][1]["content"] == "Will Brooklyn prices rise next year?")
check("max_tokens is generous enough for a reasoning model",
      sent["body"]["max_tokens"] >= 2048)
check("timeout set", sent["timeout"] == ex.TIMEOUT)

print()
if fails:
    print("FAILED %d check(s): %s" % (len(fails), ", ".join(fails)))
    sys.exit(1)
print("all checks passed")
