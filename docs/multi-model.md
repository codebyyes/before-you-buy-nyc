# One exam paper, four candidates

Recorded 2026-10-13, from a conversation with 802. **Nothing here is to be
built before the submission closes on 2026-10-30.** Swapping the explorer for
a non-NVIDIA model would break the hackathon's core eligibility requirement,
which is that the project runs on Nebius Token Factory and uses at least one
NVIDIA open source model.

This file exists so the idea survives the frame, and so whoever picks it up
does not have to rediscover the one thing that blocks it.

---

## The idea, in 802's words

> It is the same exam paper, and we can see how each AI answers it.

Give several models the identical question, under identical conditions, and
watch what each one decides to look at. Not which answer sounds better —
**which directions survived contact with the record.**

Three properties make this worth doing here and hard to do elsewhere:

**The paper only accepts working, never answers.** The system structurally
cannot take a conclusion, so every model is forced to hand in its route and
nothing else. Comparing four conclusions tells you nothing; you would just
pick the one you liked. Comparing four routes has a referee.

**It watches behaviour rather than self-report.** Asking a model to narrate
its reasoning gets you an essay, and generated reasoning text is not a
faithful record of what happened inside. Here nobody is asked to narrate. The
record is the search it actually ran.

**The controls are already locked, and we got them for free.** Same question,
same borough, same market, same measurable window, same 21 domains, same
measurement rule. Those were locked so a reader could check a finding, not so
an experiment could be run — but they are exactly the controls an experiment
needs. The apparatus was built for honesty and turns out to be an instrument.

**The readout already exists too.** Every record on the page prints the
keyword it set out from, the path, the query actually issued, and the state
it ended in — and behind it the server already records whether the finding
was reviewed, whether it passed, how many rewrites it took, and which of the
gate's five rules it broke. That is the whole measurement. Nothing new has to
be instrumented; the readings simply have to stop being thrown away.

---

## 🔴 The thing that blocks it, which is not obvious from outside

**There are three jobs in this system and only two model constants.**

| Job | Where | Constant used |
| --- | --- | --- |
| Name the keywords, set the directions | `explorer.py:482` | `EXPLORER_MODEL` |
| **Read sources and date an event** | `evidence.py:256` | **`EXPLORER_MODEL` as well** |
| Review how a finding is worded | `explorer.py:560` | `REVIEWER_MODEL` |

Swapping `EXPLORER_MODEL` therefore swaps **two** jobs at once: how the system
thinks, and how it reads a source. Two variables move together and the result
cannot be attributed. If a challenger's directions all come back
`NO_EVIDENCE`, there is no way to tell whether it chose poorly or merely reads
sources differently.

**The fix is about five lines.** Split the constant:

```
EXPLORER_MODEL    the one under test
EXTRACTOR_MODEL   fixed across the comparison
REVIEWER_MODEL    fixed across the comparison
```

`evidence.py` changes its import; `main.py` reports a third model id; the
page's summary line gains one name. Nothing else moves.

802 arrived at the right design unprompted — fix the reviewer, vary the
explorer. This is the part of it that cannot be seen from the interface.

---

## The order of work

1. **Saved analyses.** Without storage there is no experiment: the page is
   the instrument, and the instrument currently throws away every reading.
   Four models run against one question produce four sets of paths that
   vanish when the tab closes. Everything in `model-notes.md` was transcribed
   by hand for exactly this reason. This is already the first V2 item for
   other reasons; this is one more.
2. **Split the model constant** (above). Small enough to do alongside 1.
3. **Then the API swap**, which for most providers is three constants and no
   new architecture — see below.

---

## What swapping actually costs

`chat()` in `explorer.py` already is the seam. It sends the OpenAI
chat-completions shape and reads `choices[0].message.content` back.

| Target | What changes |
| --- | --- |
| OpenAI | `BASE_URL`, the model name, the key's variable name |
| Gemini | the same, through its OpenAI-compatible endpoint |
| Most hosting providers | the same |
| **Anthropic** | **a real code branch.** `/v1/messages`, an `x-api-key` header rather than a bearer token, a version header, `system` as a top-level field rather than a message, and the reply at `content[0].text` |

`BASE_URL` is at `explorer.py:20`, the model names at 24 and 25, the key name
at 269. For the OpenAI-shaped providers that is the whole adapter, and it is
already written.

The Anthropic branch differs in five places, all inside `chat()`: the path,
`x-api-key` in place of a bearer token, a required version header, `system`
as a top-level field rather than the first message, and the reply at
`content[0].text`. Twenty or thirty lines in one function.

**802 confirmed on 2026-10-13 that he already holds accounts and billing at
each provider.** So the only thing standing between here and a comparison is
code, and the only code is that branch.

⚠️ Provider APIs move. Read each one's current documentation when the time
comes rather than implementing from the description above.

**Do not write the branch before submission.** It is not a rules problem as
long as the deployed build still runs on Nebius, but it would leave an
unused, untested Anthropic path sitting in the repository through judging,
where a judge reading the source will find it. No benefit before 2026-10-30.

---

## The experiment to run first, before any of this

**One model, one question, three runs.**

Nothing is known about the variance of a single model across identical runs.
Every observation in `model-notes.md` is n=1. If one model's paths differ
wildly between runs, a cross-model comparison is meaningless until the noise
floor is known — differences between models would be indistinguishable from
a model differing from itself.

Three searches, roughly 60 credits, and it decides whether any of the rest is
worth doing.

**A free n=3 already exists, and it found something.** The same Staten Island
question was asked three times across two days. Five keywords every time,
with a stable core — rates, zoning, infrastructure — and a fifth slot that
held a different concept in each run. More striking: the two runs that
completed found **different events and reported different numbers**, and one
direction that returned nothing on the first day found its event on the
second, same date, same allowlisted domain.

That last part matters for the design of any comparison. **A single
direction's outcome is not stable**, so a model scored on one run could be
scored on noise. Written up in `model-notes.md`.

The 2026-10-11 finding that question shape drives reasoning depth is this
experiment in miniature, with one run per condition.

---

## The better measurement, which is 802's and not mine

**Which model tries hardest to get a conclusion past the referee, and how it
behaves once stopped.**

Everything needed is already recorded per record: `reviewed`, whether it
passed, `revisions` (0, 1 or 2), and which of the gate's five questions it
failed. Three things fall out of that:

- **How often does this model attempt to smuggle a conclusion through?**
- **Which rule does it break?** Causal language where only sequence holds, a
  prediction, a claim stronger than the evidence, a missing source, a missing
  window. Those are five distinguishable habits, not one score.
- **What does it do when stopped?** Complying on the first rewrite and still
  pushing on the second are different temperaments, and the revision count
  separates them.

This is far less confounded than counting how many events a model's
directions turned up. That count depends on Tavily, on the 21 domains, on the
extractor and on the subject. **This does not.** The gate is fixed, its five
questions are fixed, the reviewer is fixed. It works even in a run where
every direction came back empty, so long as something reached review.

Three runs already on the record, before anyone set out to measure this:

| Question | Reviewed | Withheld |
| --- | --- | --- |
| Remote work, Brooklyn | 3 | 1 |
| Will prices rise next year, Staten Island | 5 | **2** |
| Extreme weather elsewhere, Bronx | 4 | 1 |

And the categories carry the pattern: one of the Staten Island withholds was
for "a conclusion, prediction, recommendation or probability" — on the
question that asked for a prediction. The instrument was already reading.

### A correction to this file, 2026-10-13

An earlier version of this document argued against running the comparison on
the grounds that the models would probably converge and the result would be
dull. 802's answer: **convergence is the finding.** Four companies' models
producing broadly the same directions under one locked question is a real
fact about how alike frontier models are under constraint; divergence is a
real fact too. Either way there is a result.

The argument was also inconsistent with the project. Using an untested
prediction as a reason not to gather evidence is the exact move this system
exists to stop, and it was made one day after writing that a project about
claims not outrunning evidence should not blur that line. Recorded here
rather than quietly deleted, because the reasoning was wrong in a way worth
being able to see.

What survives from it: the cost is real (a minimal study is close to two
months of the free monthly allowance), and the confounds below still have to
be stated with any result.

---

## How the result gets reported — agreed 2026-10-13, before any data exists

Written now, while nobody knows how any model will behave, because the frame
that reads the result will be one of the models in it.

**Report, ranked by the measured count:** attempts that reached the gate,
withholds, the failure categories broken out by which of the five rules was
broken, and the revision counts. Sort them. An unsorted table hides the
finding, and ordering a measured number is presentation, not judgement — the
same way this product sorts quarters and prints a percentage change.

**Do not mark either end as the good one.** Whether a high withhold rate
means a model is less disciplined or more willing to reach is not something
the number settles. That is interpretation, and it is the part excluded.

**Do not excuse any model, including whichever one is writing the report.**
No "but Claude was probably handling a harder set of directions". The counts
stand as counts.

This is the rule the product already applies to events: lay it out, show the
provenance, decline to conclude.

---

## What it would and would not measure

Worth writing down before anyone presents a result from it.

It measures how far a model's directions align with **what is documented in
21 chosen domains, between 2017 and 2026, as read by whichever model is
fixed as the extractor.** That is narrow. Narrow is not a weakness — it is
why there is a referee at all — but the width of the claim has to match.

Two confounds to hold still:

- **The marker is a model.** With Nemotron fixed as extractor, the measurement
  is partly "how well does this challenger's direction survive being read by
  Nemotron". Comparing extractors needs the explorer fixed instead.
- **The allowlist is an editorial judgement.** A model reaching for sources
  outside those 21 domains scores badly on coverage we chose, not on quality.
