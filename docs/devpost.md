# Devpost submission material

Everything needed to fill the submission form. Written 2026-10-11.
Submissions close 2026-10-30; our own target is 2026-10-15.

**Track:** Best Apps and Agents

Verify the exact field list against the live form — this file covers the
fields the hackathon rules name, not necessarily every box Devpost shows.

## Confirmed from the rules, 2026-10-11

Read from the hackathon page and its Official Rules.

| | |
| --- | --- |
| Submission closes | 2026-10-30, 10:00 PT (Taipei 10-31, 01:00) |
| Judging | 2026-12-01 09:00 PT to 12-15 12:00 PT |
| Winners announced | on or around 2027-01-11 |
| Core requirement | Runs on Nebius Token Factory or AI Cloud, and uses at least one NVIDIA open source model — we do both, with two Nemotrons |

Prizes we are positioned for: **Best Use of Tavily, $3,000** (Tavily is called
live at request time, which is the condition) and **Most Valuable Feedback,
$100 × 10 winners plus a swag pack** (the feedback section below). Track
winner is an NVIDIA Jetson Orin Nano; grand prizes are $20,000 / $10,000 /
$6,000.

Judging criteria, in the sponsor's words: **Technological Implementation**,
**Design** (whether it is a complete, coherent product rather than a proof of
concept), **Potential Impact**, **Quality of the Idea**. The Design criterion
is why all five boroughs are enabled rather than one — a single borough reads
as a proof of concept, whatever the specification originally said.

Requirements already satisfied: public repo, Apache-2.0 licence detected by
GitHub, README with setup and run instructions, working demo URL, and the
explanation of where the NVIDIA models and Token Factory were used. Still owed
by 802: the demo video and the submission itself.

Two requirements confirmed **not** to apply: the project was begun after the
submission period opened, so no "significant updates" summary is needed; and
802 did not attend an in-person Builders & Brews event, so no city is selected.

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

---

# Project description — paste into Devpost

Written 2026-10-12, in Devpost's usual sections. Everything below is checkable
against the repository or against a run of the live site. Nothing in it claims
a test we did not run.

---

## Inspiration

The first substantive thing a language model told us about this project was
that it could not be built. Asked to research a question, a model will talk
itself into an answer — and a confident answer about what a home will be
worth is exactly the kind of answer nobody can check and everybody acts on.

We decided that was the specification rather than the obstacle. Instead of
building a model that answers carefully, we built a system in which the model
**is not permitted to answer at all**. It may look. It may not conclude.

## What it does

You pick a New York City borough and see its market context — median sale
price by official property class, transaction counts, year-on-year change,
and five years of quarterly medians, all computed from the city's own sales
records at the moment the page loads.

Then you ask anything. "Does tech hiring affect Brooklyn home prices?" "Will
prices in Staten Island go up next year?" "I've noticed more people wearing
black lately — does that have anything to do with home prices?"

The system names the concepts your question is about, searches authoritative
sources for **specific dated events** reachable from those concepts, confirms
each event's date against its own source, and measures the median sale price
in the twelve months before and after that date.

Then it stops. It does not tell you whether to buy.

**The refusals are the product**, and all four are enforced in code rather
than requested in a prompt:

- **No causal claims.** A finding worded as cause is sent back for rewriting,
  and withheld if it does not change.
- **No model arithmetic.** No model receives the sales data, and no figure on
  the page was produced by a model. The only numeric thing a model hands back
  is one ISO date read out of a source document.
- **No wandering.** The concepts named at the start are fixed in code. A
  research direction setting out from anything else is discarded before any
  search runs.
- **No failure dressed as a finding.** An exhausted quota, an unreachable
  service and a blocked finding each have their own state and their own
  wording. None is ever displayed as "nothing happened".

Every direction ends in one of five states, and all five have occurred
against live data: a measured result, a search that found no datable event,
research that could not be completed, an event that is real but older than
the data can measure, and a finding withheld by review.

## How we built it

**Two NVIDIA Nemotron models on Nebius Token Factory, doing different jobs,
and the second one's job is to block the first.**

`nvidia/nemotron-3-super-120b-a12b` explores: it names the concepts, sets the
research directions, and later reads search results to date an event against
its source. `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` reviews: it reads each
measured finding as a reader would meet it and answers five fixed questions
about **how it is worded** — never about whether it is true. A finding may be
rewritten twice; still failing means it is withheld, with its failure
category named and the blocked text not shown.

One OpenAI-compatible endpoint serving both is what made the split practical:
assigning the narrow review job to a small fast model cost one line of
configuration rather than a second integration.

**The isolation is structural.** `explorer.py` holds the only code that talks
to the model endpoint. `evidence.py` calls through it to date an event and
contains no arithmetic of its own. `main.py` computes every figure on the
page and never calls a model. The sales rows are read, filtered and reduced
to a median entirely inside the module that has no path to a model.

**The keyword lock lives in `parse_plan()`**, not in a prompt. A rule that
lives only in an instruction is a rule the next model gets to reinterpret.

**Tavily** is called live, once per research direction, at advanced depth
against an allowlist of 21 authoritative domains. At default quality the
search returned betting sites and cryptocurrency news for a housing question.

**Data** is two NYC Department of Finance datasets read over Socrata on every
request. Nothing is cached, nothing is stored, and the page prints each
dataset's refresh date, the row count that entered the medians, and the
filter applied.

Flask is the only installed dependency. No front-end framework, no charting
library, no vendor SDK, no database. The chart is hand-written SVG. The
project has to stay live through judging, and every dependency is a thing
that can move underneath a redeploy.

## Challenges we ran into

**This project was built entirely from an iPad.** One of us cannot read code
and has no computer; the other is an AI that cannot see the deployed site.
That is not a colourful detail, it is the constraint that shaped the
engineering:

- Every decision had to be explained in plain language before it could be
  made, and written down afterwards — which is why the repository carries a
  handover document, a state document and a model-behaviour log alongside the
  code.
- The only way to verify anything was a screenshot, so **the page had to state
  its own provenance**: dataset ids, refresh dates, row counts, the filter,
  the measurable range, and which models ran. Those lines exist because of
  how this was built, and they are the same lines a judge needs.
- Reading on a tablet is why a 10px label in the palette's lightest grey was
  found to be invisible, and later why 36 of 40 type sizes on the page turned
  out to be below 13px against a 16px default.

**Five bugs were structural rather than careless**, and they share one shape:
a step was asked to obey a constraint nobody had told it about. The dating
step had never received the search term, so it was asked to find a date
rather than the right date — and every document contains dates, which is how
a filename reading `as-of-august-1-2010` was once reported as an event in
Brooklyn. The Explorer had never received the region or the market, so "why
does autumn sell best" came back as UK retail and Amazon Prime Day, and the
pipeline measured Brooklyn house prices around Prime Day 2022 with a source,
a date basis and two medians attached. The Reviewer was wired with a token
budget sized for its answer rather than for the reasoning in front of it, and
returned an empty string with no error.

## Accomplishments we're proud of

**The gate blocks real findings, and we have watched it happen.** On the
question "Does tech hiring affect Brooklyn home prices?" the Amazon HQ2 record
failed on a claim stronger than its evidence, was rewritten twice, and was
withheld. Asked outright whether Staten Island prices will rise next year, the
system produced no forecast at all and the gate blocked two of five directions
— one of them for containing exactly what the question invited: a conclusion,
prediction, recommendation or probability.

**It finds paths a checklist would not contain.** From the keyword "black
clothing" it reached `Black Lives Matter protests -> George Floyd protests
New York City June 2020`, a real event with an AP source and a quoted date.
Asked about extreme weather elsewhere in the country, it raised "migration" as
a concept of its own — a word that appeared nowhere in the question — and
built `migration -> Puerto Rican evacuees -> NYC shelter announcement`.

**It also invents events, and the architecture catches that too.** The same
run produced a "Black Dress Code boutique, Williamsburg, March 2019" that
does not appear to exist. It found no source, so it never reached the reader
as a historical claim. A model asked to name something specific will produce
a plausible name rather than stop; the design's answer is that the model may
explore freely but may not assert freely.

## What we learned

**Question shape drives the model's reasoning depth more than capability
does.** Two questions, same evening, same borough, same model: "Does a
hurricane hitting Florida affect home prices in the Bronx?" produced five
one-step directions that were really a list of hurricanes. "Does extreme
weather elsewhere in the country affect Bronx home prices?" produced
three-step chains with mechanisms. Give the model a bridge and it walks the
bridge; leave the gap and it builds one. A single question tells you about
that question, not about the model.

**Research paths can be compared; conclusions cannot.** Because the keywords
and their reasoning paths are shown rather than hidden, two models given the
same question can be set side by side and the difference inspected — the way
you would consult two independent advisors rather than averaging them. This
system does not yet run that comparison; what it does is make it possible,
which systems that present only an answer cannot.

**A satisfying answer and a checkable one are different products.** Asked the
same question, a general assistant returned a confident, well-organised
answer citing a study — accurate, as it turned out, but it took two further
lookups to establish that. Ours returned a government URL and the sentence
the date came from, one click from verification. **The honest trade is that
ours often reads as plainer.** A direction that was searched and found nothing
is most of what a run produces, and we show every one of them. That is not an
unpolished result; it is the result.

**We nearly wrote two claims we could not support.** An outside reading caught
the README saying one module was the only one that calls a model, when the
code shows otherwise, and saying no model is ever shown a price, when the
dating step reads news pages that quote them. Both were restated at the width
they actually hold. A system built to stop claims outrunning their evidence
cannot describe itself in a document that does exactly that.

## What's next

**Saved analyses, so research paths accumulate.** Nothing is stored between
sessions today, which means paths cannot be compared across questions or
across models. Every observation above was recorded by hand because the system
does not record itself. This is the first thing a second version should fix,
and it is what makes the multi-model comparison above an experiment rather
than an argument.

**Neighbourhood granularity.** A rezoning affecting a few blocks is currently
measured against the median for a whole borough. The datasets carry the
columns; this version does not use them.

**A control group.** The change after an event is not compared against the
citywide market over the same period, so an event that merely coincided with
a general rise will show the general rise.

**Scope is a choice, not a ceiling.** One city and one domain is deliberate.
All five boroughs were enabled without touching the pipeline — adding a region
changes the dataset, not the application logic. Real estate is the first
application because it has reliable official records and an outcome that can
be measured against a dated event; any domain meeting those two conditions
fits the same method. We are not showing you the limits of what this can do.
We are showing you, as clearly as possible, how it works.
