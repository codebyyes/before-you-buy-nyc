# Devpost submission material

Everything needed to fill the submission form. Written 2026-10-11.
Submissions close 2026-10-30; our own target is 2026-10-15.

**Track:** Best Apps and Agents

Verify the exact field list against the live form — this file covers the
fields the hackathon rules name (spec section 20), not necessarily every box
Devpost shows.

---

## Built With

The tag list for Devpost's "Built With" field. Lowercase, hyphenated, as
Devpost expects:

```
python, flask, nvidia-nemotron, nebius-token-factory, tavily,
nyc-open-data, socrata, render, github, javascript, html, css, svg
```

**Nothing else.** No front-end framework, no charting library, no vendor SDK,
no database. The only installed dependency is Flask; everything else in the
Python is the standard library, and the page loads no external script at all.
The five-year trend chart is hand-written SVG.

This is a deliberate choice rather than a shortfall. The project must stay
live and working through judging (2026-12-01 to 12-15), and every dependency
is a thing that can move underneath a redeploy. The deployment log on
2026-10-10 showed `openai-3.28.0` installed — a package whose major version
moved during this project — for what amounted to one POST request. It was
removed.

---

## Where each technology is used

**NVIDIA Nemotron** — two models, two jobs, neither ever shown a price.

| | Explorer | Reviewer |
| --- | --- | --- |
| Model | `nvidia/nemotron-3-super-120b-a12b` | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` |
| Job | Names the concepts behind the question, sets the research directions, dates events against their sources, rewords a rejected finding | Judges how a finding is presented, against five fixed questions |

Both identifiers came from `client.models.list()`; the capitalisation rules
differ between them and neither is guessable from the catalogue display name.

**Nebius Token Factory** — the only Nebius service used, and the one that
makes the two-model split practical. One OpenAI-compatible endpoint
(`https://api.tokenfactory.nebius.com/v1`) serves both a 120B explorer and a
30B reviewer, so assigning the narrow review job to a small fast model cost
one line of configuration rather than a second integration. The region-neutral
endpoint is used because the console warns that region-specific routing may
change without notice.

**Tavily** — called live at request time, once per research direction, at
advanced depth against an allowlist of 21 authoritative domains. No result is
cached or pre-computed. The allowlist is a requirement, not tuning: at default
quality the search returned betting sites and cryptocurrency news for a
housing question.

**NYC Open Data (Socrata)** — two official NYC Department of Finance datasets,
queried live on every request, nothing stored. `w2pb-icbu` (Citywide
Annualized Calendar Sales, 2016-01-01 to 2025-12-31) and `usep-8jbt` (Citywide
Rolling Calendar Sales, the most recent twelve months).

**Flask / Python standard library** — three endpoints, no streaming, no
websocket, no polling. `main.py` computes every figure and calls no model.

**Render** — free tier, auto-deploying from GitHub `main`.

---

## The core claim

Do not drift from this:

> The system searches the official historical record for events relevant to
> the user's question, shows what followed with every source attached, and
> refuses to predict, recommend, or state a probability.
>
> **AI explores. Evidence verifies. Humans decide.**

Three concrete facts, all true and all on the record:

1. **Two Nemotron models, and the second one's job is to block the first.**
   It blocked a real finding on its first live run — the Amazon HQ2 record
   failed question 5 (a claim stronger than the evidence), was rewritten
   twice, and was withheld.
2. **"The AI never touches a number" is enforced by file.** `evidence.py`
   cannot reach a price; `main.py` asks no model anything. It is structure,
   not self-discipline.
3. **The keyword lock lives in `parse_plan()`, not in a prompt.** A research
   direction citing a concept outside the committed list is discarded before
   any search runs.

**Scope framing (required by the rules):** one city and one domain is a
deliberate choice, not a limit of the framework. All five boroughs were
enabled without touching the pipeline — adding a region changes the dataset,
not the application logic. Real estate is the first application because it has
reliable official records and an outcome that can be measured against a dated
event; any domain meeting those two conditions fits the same method.

---

## Platform feedback — eligible for a bonus award

The rules make the feedback section itself eligible for a bonus, so it is
written properly rather than left blank. Two findings from live use:

**Silent empty responses from reasoning models.** Nemotron 3 Super spends
tokens reasoning before answering, and the reasoning is billed against the
same budget as the answer. A call with `max_tokens=20` returned
`content: ""` with `finish_reason: "stop"` and no error; the usage object
showed 35 reasoning tokens consumed and 5 remaining. A developer meeting this
has no indication of what went wrong. The same bug bit us a second time when
the Reviewer was first wired at 256 tokens and came back empty on every call.
A distinct finish reason when the budget is exhausted during reasoning would
prevent both.

**Inconsistent model identifiers.** The two models' API identifiers follow
different capitalisation conventions, and neither matches its catalogue
display name. `client.models.list()` is the only reliable source. Making the
catalogue show the API identifier would save every developer this step.

**What worked well.** Nemotron 3 Super returned bare JSON on every call, with
no preamble and no markdown fencing, so the pipeline could consume its output
directly. Given a vague question it produced seven research directions and
given a tightly constrained one, five — it was never told how many to produce
and did not pad. Nemotron 3 Nano, given a finding containing four deliberate
presentation violations, returned `FAIL 1 2 3 4` in four tokens. For a gate
whose entire job is to pass or block, that terseness is exactly right, and a
30B model is sufficient for it.

---

## Still owed by 802

- YouTube demo video, under three minutes, publicly visible, no third-party
  trademarks or copyrighted music. The video is a video; the parts showing the
  program running are screenshots taken while it runs.
- Submit on Devpost.
- Confirm screenshots for Bronx, Queens and Staten Island.

The demo script is written only after the whole thing has been verified, not
before.
