# Before You Buy NYC — Product Specification

**AI explores. Evidence verifies. Humans decide.**

As of 2026-10-11 · Nebius × NVIDIA Global AI Hackathon, Best Apps and Agents

> This is the English product specification, written 2026-10-11 20:00.
> The live, editable copy is a Claude doc:
> https://claude.ai/code/artifact/8b424939-b03d-4dd0-a7bb-0e27f491258e
> This file is the copy that travels with the repository, so a frame with no
> access to that link still has it. **The README (action two in `NEXT.md`) is
> built from this document** — do not write the README from memory.

---

## What this is

Before You Buy NYC answers a question about New York City housing by finding
dated events in the official record, showing what the market did in the twelve
months after each one, and refusing to say why.

A person types a question — "Does tech industry hiring affect Brooklyn home
prices?" The system names the concepts the question is about, searches
authoritative sources for specific past events reachable from those concepts,
confirms each event's date against its source, and then measures the median
sale price in the twelve months before and after that date from New York
City's own sales records.

It does not predict. It does not recommend. It does not state probabilities.
It never says one thing caused another; it says what followed, and shows the
source and the window so the reader can judge for themselves.

The refusals are the product. Four things the system will not do, enforced in
code rather than requested in a prompt:

- **No causal claims.** The interface says "what follows each event, not what
  caused it". A finding worded as cause is sent back for rewriting, and
  withheld if it does not change.
- **No model arithmetic.** Every figure on the page is computed in Python from
  official rows. No model is given the sales data, and no figure shown is
  one a model produced. A model does read search results that may quote a
  price; it never receives the dataset those figures are computed from.
- **No wandering.** The concepts named at the start are fixed. A research
  direction that sets out from anything else is discarded before any search
  runs.
- **No failure dressed as a finding.** An exhausted quota, an unreachable
  service and a blocked finding each have their own state and their own
  wording. None of them is ever displayed as "nothing happened".

---

## Scope

The system answers questions about residential property sales in the five
boroughs of New York City, over events dated 2017-01-01 or later.

| | |
| --- | --- |
| Region | Manhattan, Bronx, Brooklyn, Queens, Staten Island — one at a time, chosen before the question |
| Market | Residential property sales, nine eligible building-class categories |
| Measurable period | 2017-01-01 to 2026-08-31 |
| Price basis | Recorded sale price, transactions of $100,000 or more |
| Measurement | Median sale price, twelve months before the event date against twelve months after |
| Question length | 500 characters |
| Records per question | At most 10 |

The measurable period is not a preference. The annualized dataset begins
2016-01-01, and an event needs a complete twelve-month window behind it to be
measured, so the first measurable date is twelve months after the data begins.
An event the system finds, dates and sources but which falls before that floor
is reported as real and unmeasurable rather than quietly dropped.

Out of scope in this version: neighbourhood granularity, commercial property,
rentals, cities other than New York, user-selected time windows, and any
stored state between sessions. Nothing a person types is kept after the
response is sent.

---

## Architecture

```
1 · Explore                          2 · Find and date
explorer.py · Nemotron Super 120B    evidence.py -> explorer.chat · Super 120B
Names the keywords, sets the    ->   Searches 21 authoritative domains.
directions. The keyword list is      Dates one event against its own source.
then locked in code.                 Sees: the search term and the sources.
Sees: the question, region,
market, dates.                                     |
                                                   | one dated, sourced
   +-----------------------------------------------+ event per direction
   v
3 · Measure                          4 · Review
main.py · no model is called         explorer.py · Nemotron Nano 30B
Median of the 12 months before  ->   Five fixed questions on how it is worded.
and after. Computed in Python        Two rewrites, then the finding is withheld.
from official rows.                  Sees: the finding. Never a number.
Sees: prices. Asks no model
anything.

Enforced by file: main.py holds every figure and makes no model call; the
two modules that do call one are never handed the sales rows.
```

Three modules, and the division between them is the design. `explorer.py`
holds the only code that talks to the model endpoint; `evidence.py` calls
through it to date an event and contains no arithmetic of its own; `main.py`
computes every figure and never calls a model.

Spec section 13 — "the AI never touches a number" — is therefore structural
rather than a matter of self-discipline, but the claim has to be stated at
the width it actually holds. A model does read search results, and a news
page may quote a price. What no model receives is the sales dataset, and what
no model produces is any figure the page displays: the rows are read,
filtered and reduced to a median entirely inside `main.py`, which has no path
to a model. The only numeric thing a model hands back in this system is one
ISO date read out of a source document.

`templates/index.html` holds all presentation and the front-end JavaScript.
Nothing in the Python writes HTML.

---

## The pipeline

Three HTTP requests, no streaming. The first column never redraws, so asking a
second question does not refetch the city's data.

1. **`POST /confirm`** — market context for the chosen borough from NYC Open
   Data: median and transaction count by building class, year-on-year change,
   and twenty quarters of median price. Takes 20–30 seconds. Calls no model and
   spends no search credit.
2. **`POST /explore`** — the question goes to the Explorer model, which returns
   the keywords and the research directions. The keywords are then locked.
   Takes 20–40 seconds. Calls one model and spends no search credit.
3. **`POST /evidence`** — issued automatically by the page. Each direction is
   searched, each result is dated against its source, each dated event is
   measured from official rows, and each measured finding goes through the
   presentation gate. Takes 60–120 seconds. This is the only step that spends
   search credit.

There is no server-sent events stream, no websocket and no polling. Two
ordinary POST requests carry the whole interaction, which means there is no
partial state to reconcile if a phone drops its connection mid-question.

Every wrong door opens on the start page with a neutral notice. A tab left on
`/confirm` overnight and refetched with GET returned 405 Method Not Allowed in
testing; `/confirm` now accepts GET, and the 404 and 405 handlers render the
start page and explain that nothing was stored.

---

## Stage one: exploration, and the lock

The Explorer model is given the question together with what the question is
about, names the concepts it is really asking after, and may then only work
from those concepts.

It receives four lines, not just the question:

```
REGION: Brooklyn, New York City
MARKET: residential property sales
MEASURABLE PERIOD: 2017-01-01 to 2026-08-31

QUESTION: Does tech industry hiring affect Brooklyn home prices?
```

The context is there because a question alone is not enough. Asked only "why
does autumn sell best", the model returned five directions about UK retail
sales, earnings calls and Amazon Prime Day, and the pipeline went on to measure
Brooklyn house prices around Prime Day 2022 — with a source, a date basis and
two medians. The region, the market and the data window were known to the
system and passed to nothing.

It returns keywords, a recurrence flag, and directions:

```json
{"keywords": ["tech hiring", "Brooklyn home prices"],
 "recurring": false,
 "directions": [{"from": ["tech hiring"],
                 "path": "tech hiring -> office demand -> local wages -> prices",
                 "query": "Amazon HQ2 Long Island City announcement November 2018"}]}
```

Four rules make this stage what it is:

- **Keywords are short concepts, not search phrases.** "interest rates",
  "umbrellas", "school districts" — the way a person says them out loud. They
  are what the reader checks the findings against, so they stay in the language
  the question was asked in.
- **Events, never trends.** Every direction must end at something a named party
  did on a particular day. "Hiring grew" and "the market cooled" have no date
  and cannot be measured, so the prompt carries worked examples of stopping one
  step too early: "Brooklyn tech employment growth 2018" against "Amazon HQ2
  Long Island City announcement November 2018".
- **No pairing off.** A keyword may feed several directions, one, or none. An
  unused keyword stays in the list as an honest record of where the system
  considered looking.
- **Distance is allowed.** From the keyword "black clothing", the path
  "Black clothing -> protest movements -> market instability" is a valid thing
  to search. Unusual directions are not filtered out; they are searched and
  then reported honestly, including when they find nothing.

The lock is the part that matters. Once the keywords are returned they are
fixed, and `parse_plan()` drops any direction citing a concept that is not
among them — before a single search runs, and before the reader sees anything.
The count of discarded directions is reported rather than hidden.

This is checked in code, not requested in the prompt, because the failure it
prevents is precisely a model seeing A and setting off after B. A rule that
lives only in an instruction is a rule the next model gets to reinterpret.

---

## Stage two: evidence

Each direction is searched against an allowlist of 21 authoritative domains,
and a result only becomes a finding if one specific event can be dated from the
source text or URL.

Search is Tavily, at advanced depth, ten results per query, restricted to:

- **Federal** — federalreserve.gov, census.gov, bls.gov, hud.gov,
  federalregister.gov, gao.gov
- **New York State and City** — ny.gov, nyc.gov, hcr.ny.gov,
  comptroller.nyc.gov, council.nyc.gov, dos.ny.gov, esd.ny.gov
- **Press of record** — reuters.com, apnews.com, nytimes.com, wsj.com,
  bloomberg.com
- **New York business and local press** — crainsnewyork.com, thecity.nyc,
  gothamist.com

The allowlist and the advanced depth are both requirements, not tuning. At
default quality the search returned betting sites and cryptocurrency news for a
housing question, and the wrong event at that. Ten results rather than five
costs nothing extra, because credit is charged per search and not per result,
and the page carrying the dated sentence is often not in the first five.

The dating step is then given the search term alongside the sources, and must
satisfy four rules:

- The event must be **what the search term was looking for**. Different
  subject, different place or different period returns `found: false`.
- It must be **something that happened on a day** — a decision, a vote, a
  ruling, an announcement, a rate change, a filing, a disaster, a launch.
- **A document's own date is not an event.** Publication dates, "as of" dates,
  dataset vintages and dates appearing only in filenames do not qualify.
- The date must be **stated or clearly derivable** from the source text or URL,
  and the URL returned must be one the search actually returned — a paraphrased
  URL is rejected in code.

Returning `found: false` is a correct answer, recorded as a direction that was
searched and yielded nothing.

The search-term rule exists because of a real failure. The direction "Brooklyn
downtown luxury condo oversupply 2021-2022" produced an event dated 2008-08-01
whose stated basis was the string `as-of-august-1-2010` inside a PDF filename,
for a building on Wall Street in Manhattan. Wrong decade, wrong borough, and
not an event at all. The cause was structural: the dating step had never been
given the keyword, so it was asked to find a date rather than the right date —
and every document contains dates.

Nothing in this module computes anything. It never sees a price, and the
measurement it hands downstream is a date.

---

## Stage three: measurement

Every figure is computed in Python from New York City's own sales records. The
model supplied a date and nothing else.

For each event date, the system takes the median sale price of eligible
residential transactions in the twelve months before it and the twelve months
after it, with the transaction count on each side and the percentage change
between the two medians.

Four rules govern the arithmetic:

- **Single boundary.** The annualized dataset is authoritative up to its own
  last sale date and the rolling dataset serves everything after it. The two
  overlap in the source data, so one boundary is the only way to avoid counting
  a transaction twice.
- **Eligibility is fixed.** Nine residential building-class categories,
  transactions of $100,000 or more. The floor excludes nominal and
  zero-consideration transfers, which are recorded sales but not market prices.
- **A short window is reported as short.** When the data does not reach twelve
  months past an event, the window is cut to what exists and the months
  actually elapsed are stated. Comparing six months against twelve and calling
  it a year is the misreading this rule exists to prevent.
- **One fetch per question.** Event windows overlap heavily, so the union span
  is barely wider than the widest single window and all of them are served by
  one query. This is a better-written query, not a cache.

The five-year trend line in the first column is twenty quarters, one point per
quarter, drawn as a line rather than bars. Medians sit in a narrow band, so
zero-based bars would all look identical while non-zero-based bars would
exaggerate; a line may sit on a non-zero axis, and the axis range is printed on
the chart so nothing is concealed. The incomplete final quarter is drawn
dashed.

NYC Open Data revises these datasets retroactively. Quarterly figures verified
on 2026-10-08 differed slightly from the same figures on 2026-10-10 — three to
five transactions, a few medians. This is the publisher correcting the record,
not a defect, which is why the page prints each dataset's refresh date.

---

## Stage four: the presentation gate

A second model reads each measured finding as a reader would meet it and
answers five fixed questions about how it is worded. It is never asked whether
the finding is true.

The gate exists against one named failure. The first substantive response this
project got from a language model was that it could not be built, because a
model asked to research a question will talk itself into an answer. The
Explorer may still reason toward whatever it likes. What it may not do is be
the party that decides its reasoning has become a result.

The five questions, as the Reviewer receives them:

1. Does every presented event carry an identifiable source?
2. Is causal language used where only sequence is established?
3. Does the result contain a conclusion, prediction, recommendation or
   probability?
4. Is the observation window stated?
5. Is the claim stronger than the underlying evidence?

A finding fails if 1 or 4 is answered no, or if 2, 3 or 5 is answered yes. The
reply is one word, PASS or FAIL, followed by the failing numbers and nothing
else.

How it is bounded:

- **Only findings on their way to becoming a result go through it.** The other
  four states never reach the gate.
- **Five questions, fixed.** No sixth question and no rewording into an
  open-ended check — an open re-check hands substantive judgement back to a
  model, which is what the narrow scope exists to prevent.
- **At most two revisions,** and a revision may change only wording. The date,
  the source, the URL and every figure were produced by the evidence and by the
  program; the rewrite cannot reach them.
- **Still failing means withheld.** The state becomes
  `EVIDENCE_FOUND_BUT_WITHHELD`, and the page names the failure categories and
  their count without reproducing the blocked text. Publishing what failed the
  gate would be a way around the gate.
- **A gate that cannot be reached is not a gate that blocked something.** An
  unreachable Reviewer is `RESEARCH_INCOMPLETE`. The two are never displayed as
  each other.
- **The wording never apologises.** A withheld finding is the system working as
  specified. The test suite scans every reason string for "sorry",
  "unfortunately", "unable", "apolog", "regret" and "fail", and fails the build
  if any of them appears.

It blocked something on its first live run. For the question "Does tech
industry hiring affect Brooklyn home prices?", the Amazon HQ2 record failed
question 5 — a claim stronger than the evidence — was rewritten twice, and
still did not pass. The page showed the direction, the keyword it came from and
the reason category, and withheld the finding.

The summary line at the foot of each analysis is counted from the server's
record of the gate actually running, not inferred from the final states:

```
4 measured · 4 passed presentation review · 1 withheld by review · 1 not completed
```

---

## The five states

Every research direction ends in exactly one of five states. All five have
occurred against live data.

| State | What it means | What the reader sees |
| --- | --- | --- |
| `RESULT` | Dated, sourced, measurable, and it passed the gate | Event, date, date basis, source link, and the before-and-after medians |
| `NO_EVIDENCE` | The search ran and the sources held no datable event | How many sources were searched, and that this does not mean nothing happened |
| `RESEARCH_INCOMPLETE` | The research could not be completed: missing key, exhausted quota, timeout, unreachable service, unreachable reviewer — or a reply from the extraction step this system cannot use | The failure, worded for the step it happened at, and the original error |
| `EVENT_OUTSIDE_MEASURABLE_RANGE` | The event is real and dated but falls before 2017-01-01 | The event in full, plus why this data cannot measure it |
| `EVIDENCE_FOUND_BUT_WITHHELD` | It did not pass presentation review within two revisions | The failure categories and their count, never the blocked text |

A sixth label, `PENDING`, is deliberately not one of the five. The five are end
states; `PENDING` is the honest label for the gap between the Explorer
finishing and the evidence layer starting.

### The same question does not give the same directions

Eight runs of one identical question produced a stable core of concepts and a
moving edge, and the two that completed found different events and reported
different figures. This is the behaviour section 7 describes between models,
observed within one. It is not a defect: a run reports the directions it
searched, never the directions that exist, and both results are sourced and
measured identically. The cause is open — `tools/variance.py` separates
sampling from the alternative and has not been run. Amendments A16 and A17
carry the full account.

Two rules hold the set together.

**No failure may be reported as an empty result.** `NO_EVIDENCE` says this
search found nothing; `RESEARCH_INCOMPLETE` says the research could not be
completed. An exhausted quota is a fact about us, not a fact about the
historical record. The test suite scans every reason string to confirm that no
failure path has acquired "no evidence" wording.

The line is drawn at who is speaking. `NO_EVIDENCE` is reached one way only:
the extraction step read the sources and reported that they held no datable
event. Every other outcome of that step — a reply that is not a result object,
an event returned without its date or its source, a source address that was
not among the pages the search returned — is this system coming back empty,
not the record. The sources may well have held something; we never learned
what. Those end as `RESEARCH_INCOMPLETE`, which also makes the whole analysis
incomplete, because a direction we dropped is a direction the reader did not
get an answer on.

**One incomplete direction makes the whole analysis incomplete,** and it is
said once at the top rather than only in the margin of the direction it belongs
to. A reader who scrolls past one pink box should not come away believing they
saw a complete answer.

The states also carry where the failure happened, which the interface needs in
order not to contradict itself. An early version printed an event, its date, a
quoted basis and a comptroller.nyc.gov link, and underneath them a red box
reading "nothing was searched here" — because the search had succeeded and the
measurement had failed, and there was only one piece of failure wording. Each
failure is now worded for its own step, and the local harness fails if any
record shows a source while claiming nothing was searched.

---

## Data sources

Two NYC Open Data datasets, read live over Socrata on every question. Nothing
is cached and nothing is stored locally.

| Dataset | Id | Covers | Rows |
| --- | --- | --- | --- |
| Citywide Annualized Calendar Sales | `w2pb-icbu` | 2016-01-01 to 2025-12-31 | 845,607 |
| Citywide Rolling Calendar Sales | `usep-8jbt` | 2025-09-01 to 2026-08-31 | 82,345 |

Row counts and date ranges are read from the datasets themselves at request
time, not hard-coded, and both refresh dates are printed on the page. The
annualized set gives the long comparable history; the rolling set gives the
most recent months. Each date is served by exactly one of them.

Search is Tavily at advanced depth against the 21-domain allowlist. Both the
model endpoint and the search endpoint are called over the Python standard
library — no vendor SDK — for a specific reason: the 10/10 deployment log
showed `openai-3.28.0` installed, a package whose major version moved during
this project. A redeploy during the 12/01–12/15 judging window is not the
moment to discover an API has changed. Both endpoints are OpenAI-compatible or
plain JSON POST, and the two lines an SDK saves are not worth that risk.

Sources appear in the interface as live links to the page the date came from,
with the sentence or URL fragment the date was derived from quoted beside it.

---

## Models and infrastructure

Both models are NVIDIA Nemotron, both served by Nebius Token Factory, and they
do different jobs.

| | Explorer | Reviewer |
| --- | --- | --- |
| Model | `nvidia/nemotron-3-super-120b-a12b` | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` |
| Job | Names the concepts, sets the research directions, dates events from sources, rewords a rejected finding | Judges how a finding is presented, against five fixed questions |
| Sees prices | Never | Never |
| Decides anything numeric | No | No |

Both are reasoning models, and the reasoning is billed against the same token
budget as the answer, so every call is given `max_tokens=4096`. A small budget
returns an empty content field because the whole allowance went into thinking —
the Reviewer was first wired at 256 tokens and came back empty every time. Any
new model call in this codebase gets the generous budget.

```
BASE_URL = "https://api.tokenfactory.nebius.com/v1"
```

Both model IDs came from `client.models.list()`. Their capitalisation rules
differ from each other and neither is guessable, so they are not retyped from
memory.

| | |
| --- | --- |
| Dependency | `flask`. Everything else is the Python standard library |
| Hosting | Render free tier, auto-deploying from GitHub `main` |
| Cold start | About 50 seconds after 15 idle minutes |
| Secrets | `NEBIUS_API_KEY`, `TAVILY_API_KEY` as environment variables |
| Search cost | 2 credits per advanced search, so a ten-record question is 20 credits |
| Search allowance | 1,000 credits a month, resetting monthly — about 50 full questions |
| Per-instance guard | `SEARCH_CREDIT_BUDGET`, default 300 credits |

The per-instance guard counts in memory and the free tier sleeps after fifteen
idle minutes, so it stops one person holding the button down and nothing more.
It is not described anywhere as a real limit; a real limit needs stored state,
which this version does not have.

The search cost was measured on the account rather than estimated: 47 credits
to 55 across a single question of four searches.

---

## Interface rules

Some of what looks like styling is specification, because the wording and the
colour are where a hedge would hide.

**Sequence, never cause.** The heading above the records reads "What follows
each event, not what caused it". The word "caused" does not appear as a claim
anywhere in the interface, and a finding that uses causal language is sent back
for rewriting.

**One colour per kind of number, and colour never means direction.**

| Token | Colour | Carries |
| --- | --- | --- |
| `--fig-median` | `#1f6fb2` blue | Median price |
| `--fig-count` | `#191712` ink | Transaction count |
| `--fig-change` | `#8a3a62` plum | Year-on-year change, the same hue whether it rose or fell |

A rise and a fall share one colour, so the colour cannot say whether a number
is good news. What is prohibited is directional colour coding, not colour.

Green was asked for and rejected on measurement. Against the olive `#8a6a28`
already on the card, five candidate greens scored ΔE 11.8–14.3 in normal vision
and 3.4–4.9 in protanopia, all below the floor of 15. Green and olive are
neighbours.

**The keywords are one line, above everything, shown once.** They sit in a tray
under the question, one box per keyword, before the records. Each record then
carries its own origin chips and reasoning path as provenance beneath it. This
took four attempts: bold text (read as an event name), a labelled row (10px in
the lightest grey in the palette, invisible on an iPad), a block heading, and
finally the single line. The first three failures were a structural problem
treated as a styling problem.

**The transaction count is labelled for what it is.** The header reads "Sales
in median" — the number of transactions that entered the median — and is never
called market volume anywhere in the interface, because it is not a volume
measure.

**Model output is never trusted as markup.** Every string a model produced is
written with `textContent`. Nothing takes the `innerHTML` path.

---

## Verification

About 100 offline checks run with no network access and no spend, and a local
harness exercises the whole flow with every outside service stubbed.

`test_explorer.py` guards the parts of the prompts that are load-bearing and
the parts of the state machine that must not drift: the CRITICAL paragraph, the
black-clothing example, the relevance and trend rules, English-only queries,
the prohibition on pairing keywords to records one for one, the ten-direction
cap, the lock discarding strayed directions, verdict parsing, the two-revision
limit, and a scan confirming no withheld reason has acquired apologetic
wording.

`tools/serve_local.py` runs the two-step flow against stubs for Nebius, Tavily
and NYC Open Data, producing all five states on one page. Every price in it is
synthetic and labelled as such. Two assertions in the harness exist because of
specific bugs: that the extractor received its search term, and that the
Explorer received its context.

What has been verified against the live service, and what has not:

| | |
| --- | --- |
| Verified live | Brooklyn and Manhattan, the full two-step flow, all five states, the gate withholding a real finding |
| Not yet verified live | Bronx, Queens, Staten Island — same datasets and same code path, one confirmation each |
| Pending | Re-verification of the two prompts modified on 2026-10-11 |

The prompt re-verification is the one outstanding technical item. Both modified
prompts are flagged in code comments with the date and the reason, and the test
cases are fixed in advance: the Wall Street filename case must return
`found: false`, the Federal Reserve press-release URL `monetary20200315b.htm`
must still yield 2020-03-15, and `Brooklyn protest attire black clothing 2020`
must survive.

Five of the bugs found during development were structural rather than lapses,
and share one shape — a step was asked to obey a constraint it had never been
told about:

| Symptom | Cause |
| --- | --- |
| An event dated 2008 from a 2010 filename, wrong borough | The dating step never received the search term |
| A housing question answered with UK retail and Prime Day | The Explorer never received the region, market or window |
| The Reviewer returning an empty verdict | A token budget sized for the answer, not for the reasoning in front of it |
| A sourced event under a box reading "nothing was searched here" | One piece of failure wording for three different failure steps |
| A credit allowance spent at half the rate it was going out | Arithmetic used to overturn a measurement instead of measuring again |

The last one is worth stating plainly: the cost per search was first guessed,
then "resolved" by dividing a rough total by a half-remembered history, and the
resolution was wrong in the direction that flattered the budget. The clean
measurement settled it.

---

## Known limitations

Stated here deliberately, because a reader finds them anyway and a system about
epistemic honesty cannot be shy about its own.

**Things without events are invisible to it.** Demographic change, the slow
erosion of purchasing power, a long interest-rate cycle — any of these may
matter more than any single rezoning, but none of them happened on a particular
day, so this system cannot see them. What it can say is "here are events that
were recorded, and here is what followed". It cannot say "here is everything
that mattered".

**Events are neighbourhood-scale; the data is borough-scale.** The Gowanus
rezoning is measured against the median for all of Brooklyn. The datasets carry
`neighborhood` and `nta` columns, so finer granularity is the most valuable
thing a second version could do, but it is not in this one.

**A twelve-month window is a choice, not a finding.** Twelve months before
against twelve after is applied uniformly. Some events move a market in a
quarter and some over five years, and this system does not distinguish them.

**There is no control group.** The change after an event is not compared
against the citywide market over the same period, so an event that merely
coincided with a general rise will show the general rise. Seasonality is
likewise uncontrolled.

**An absence of evidence is reported honestly, not resolved.** `NO_EVIDENCE`
means the sources searched held no datable event. It does not mean nothing
happened, and the interface says so each time.

**The sources are an allowlist, which is a judgement.** Twenty-one domains were
chosen as authoritative. A relevant event covered only outside that list will
not be found, and the list itself is an editorial decision the system makes on
the reader's behalf.

**Coverage begins in 2016 and measurement in 2017.** Events before then — the
2008 financial crisis among them — can be found and dated but not measured, and
are reported as such rather than omitted.
