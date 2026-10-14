"""Ask the explorer the same question N times and print what changed.

    python tools/variance.py                       # 3 runs at the service default
    python tools/variance.py --runs 5
    python tools/variance.py --temperature 0       # the discriminating arm
    python tools/variance.py --question "..." --region Brooklyn

Needs NEBIUS_API_KEY. Spends model tokens and **no Tavily credit**: only the
explore step runs, never the search. That is what makes this cheap, and it is
the point - the keywords are the measurement, not an input to one.

---

The question it answers
-----------------------

Asked the identical question three times across two days, the explorer
returned five keywords every time with a stable core and a moving fifth slot
(`docs/model-notes.md`). Two readings of that:

  sampling    one process with a die in it. The request carries no
              temperature, so the service default applies, and that default
              is usually well above zero.

  something   802's reading: each instantiation is its own thing with its own
  else        ordering of what matters, and the variation is that showing.

They predict different things at temperature zero. If the variation collapses
when the die is taken away, it was the die. If it survives, it was not, and
the second reading has its strongest evidence.

Run both arms. The default arm is the control.

---

What this tool does **not** touch
---------------------------------

`explorer.py` and `evidence.py` are left alone. This file builds its own
request rather than calling `chat()`, because `chat()` sends no temperature
and adding one would be a change to the deployed system. It imports the
prompt and the context builder so that what is measured is the real thing.

🔴 Not before 2026-10-30. Nothing here breaks eligibility - it is a dev tool,
it is not deployed and it is not in the line 802 pastes into Replit - but it
has never been run against the live service, and the deadline is not the week
to find out what it does.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from explorer import (BASE_URL, EXPLORER_MODEL, EXPLORER_PROMPT, MAX_TOKENS,
                      TIMEOUT, ask_block, extract_json, parse_plan)

QUESTION = "Will home prices in Staten Island go up next year?"
REGION = "Staten Island"
DATA_FROM = "2017-01-01"
DATA_TO = "2026-08-31"


def one_run(user, temperature):
    """One explore call. Returns the parsed plan, or raises RuntimeError."""
    key = os.environ.get("NEBIUS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("NEBIUS_API_KEY is not set.")

    payload = {
        "model": EXPLORER_MODEL,
        "messages": [
            {"role": "system", "content": EXPLORER_PROMPT},
            {"role": "user", "content": user},
        ],
        "max_tokens": MAX_TOKENS,
    }
    # Omitted entirely rather than sent as null, so the default arm is exactly
    # the request the product makes.
    if temperature is not None:
        payload["temperature"] = temperature

    req = urllib.request.Request(
        BASE_URL + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"},
        method="POST")

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:200]
        raise RuntimeError("HTTP %s. %s" % (exc.code, detail.strip()))
    except Exception as exc:
        raise RuntimeError("%s: %s" % (type(exc).__name__, exc))

    try:
        text = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("response in an unexpected shape")
    if not text or not text.strip():
        raise RuntimeError("empty content, which on a reasoning model means "
                           "the whole budget went into thinking")

    return parse_plan(extract_json(text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=None,
                    help="omitted by default, which is what the product does")
    ap.add_argument("--question", default=QUESTION)
    ap.add_argument("--region", default=REGION)
    args = ap.parse_args()

    user = ask_block(args.question, args.region, DATA_FROM, DATA_TO)
    arm = ("default" if args.temperature is None
           else "temperature=%g" % args.temperature)

    print("question    %s" % args.question)
    print("region      %s" % args.region)
    print("model       %s" % EXPLORER_MODEL)
    print("arm         %s" % arm)
    print("runs        %d\n" % args.runs)

    seen = []
    for i in range(1, args.runs + 1):
        try:
            plan = one_run(user, args.temperature)
        except RuntimeError as exc:
            print("run %d  could not be completed: %s" % (i, exc))
            seen.append(None)
            continue
        words = plan.get("keywords", [])
        seen.append(words)
        print("run %d  %d keywords" % (i, len(words)))
        for w in words:
            print("         %s" % w)
        for d in plan.get("directions", []):
            print("       . %s" % d.get("path", ""))
        print()

    good = [set(w) for w in seen if w is not None]
    if len(good) < 2:
        print("Not enough completed runs to compare.")
        return

    core = set.intersection(*good)
    everything = set.union(*good)
    print("in every run      %s" % (", ".join(sorted(core)) or "nothing"))
    print("in only some      %s"
          % (", ".join(sorted(everything - core)) or "nothing"))
    print("\n%d of %d concepts were stable across %d runs."
          % (len(core), len(everything), len(good)))

    # Reporting rule agreed 2026-10-13: lay out the counts, decline to say
    # what they mean about the model.
    print("\nCounts only. Whether a stable core means the question has an "
          "obvious shape,\nor the model has a settled way of seeing it, is "
          "not something this settles.")


if __name__ == "__main__":
    main()
