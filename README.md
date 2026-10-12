# Before You Buy NYC

**AI explores. Evidence verifies. Humans decide.**

Ask a question about New York City housing. The system finds dated events in
the official record, shows what the market did in the twelve months after each
one, and refuses to say why.

Built for the Nebius × NVIDIA Global AI Hackathon — **Best Apps and Agents** track.

**Live:** https://before-you-buy-nyc.onrender.com
(free tier; the first visit after fifteen idle minutes takes about 50 seconds to wake)

---

## What it does

A person picks a borough, then types a question — "Does tech industry hiring
affect Brooklyn home prices?"

The system names the concepts the question is about, searches authoritative
sources for specific past events reachable from those concepts, confirms each
event's date against its own source, and then measures the median sale price in
the twelve months before and after that date from New York City's own sales
records.

It does not predict. It does not recommend. It does not state probabilities. It
never says one thing caused another — it says what followed, and shows the
source and the window so the reader can judge for themselves.

### The refusals are the product

Four things the system will not do. Each is enforced in code, not requested in
a prompt:

- **No causal claims.** A finding worded as cause is sent back for rewriting,
  and withheld if it does not change.
- **No model arithmetic.** Every figure on the page is computed in Python from
  official rows. No model is given the sales data, and no figure shown is
  one a model produced. A model does read search results that may quote a
  price; it never receives the dataset those figures are computed from.
- **No wandering.** The concepts named at the start are fixed. A research
  direction setting out from anything else is discarded before any search runs.
- **No failure dressed as a finding.** An exhausted quota, an unreachable
  service and a blocked finding each have their own state and their own
  wording. None is ever displayed as "nothing happened".

---

## Running it

**Requirements:** Python 3.11 or later.

```bash
git clone https://github.com/codebyyes/before-you-buy-nyc.git
cd before-you-buy-nyc
pip install -r requirements.txt
```

### Environment variables

The application needs two API keys. Without them it starts and serves the
market-context column, but any research question returns
`RESEARCH_INCOMPLETE` — which is the correct behaviour, not a crash.

| Variable | Required | What it is |
| --- | --- | --- |
| `NEBIUS_API_KEY` | Yes | Nebius Token Factory key, for both Nemotron models |
| `TAVILY_API_KEY` | Yes | Tavily key, for the live search layer |
| `SOCRATA_APP_TOKEN` | No | NYC Open Data app token. Works without one, at a lower rate limit |
| `SEARCH_CREDIT_BUDGET` | No | Per-instance search-credit guard. Defaults to 300 |
| `PORT` | No | Defaults to 5000 |

```bash
export NEBIUS_API_KEY="..."
export TAVILY_API_KEY="..."
python main.py
```

Then open `http://localhost:5000`.

No dataset download is required. The application queries the official NYC Open
Data API at runtime and stores nothing.

### Offline checks

```bash
python test_explorer.py
```

About 100 checks covering the load-bearing parts of the prompts and the state
machine. No network access, no API keys, no spend. The last line should read
`all checks passed`.

```bash
python tools/serve_local.py
```

A local harness that runs the whole flow with Nebius, Tavily and NYC Open Data
all stubbed, producing all five states on one page at
`http://127.0.0.1:8746`. Every price in it is synthetic and labelled as such.
This is a development tool and is not part of the deployed application.

---

## Where NVIDIA Nemotron is used

Two Nemotron models, both served by **Nebius Token Factory**, doing different
jobs. Neither is ever shown a price, and neither decides anything numeric.

| | Explorer | Reviewer |
| --- | --- | --- |
| Model | `nvidia/nemotron-3-super-120b-a12b` | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` |
| Job | Names the concepts, sets the research directions, dates events against their sources, rewords a rejected finding | Judges how a finding is presented, against five fixed questions |
| Sees prices | Never | Never |

```
BASE_URL = "https://api.tokenfactory.nebius.com/v1"
```

Both model identifiers came from `client.models.list()` rather than the
catalogue display names. Their capitalisation rules differ from each other and
neither is guessable.

**Nebius Token Factory is the only Nebius service this project uses.** It
serves both models through one OpenAI-compatible endpoint, which is why a
120B explorer and a 30B reviewer could be assigned to different jobs without
running two integrations. Both are reasoning models, and reasoning is billed
against the same token budget as the answer, so every call is given
`max_tokens=4096` — a small budget returns an empty content field because the
whole allowance went into thinking.

The endpoint is called over the Python standard library rather than a vendor
SDK. The project must stay live through judging (2026-12-01 to 12-15), and a
redeploy in that window is not the moment to discover an SDK's major version
has moved.

## Where Tavily is used

Tavily is called **live, at request time**, once per research direction. No
result is cached or pre-computed.

Search runs at advanced depth against an allowlist of 21 authoritative
domains — federal (federalreserve.gov, census.gov, bls.gov, hud.gov,
federalregister.gov, gao.gov), New York State and City (ny.gov, nyc.gov,
hcr.ny.gov, comptroller.nyc.gov, council.nyc.gov, dos.ny.gov, esd.ny.gov),
press of record (reuters.com, apnews.com, nytimes.com, wsj.com, bloomberg.com)
and New York business and local press (crainsnewyork.com, thecity.nyc,
gothamist.com).

Both the allowlist and the advanced depth are requirements rather than tuning.
At default quality the search returned betting sites and cryptocurrency news
for a housing question.

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
```

**The division between the files is the design.** `explorer.py` holds the only
code that talks to the model endpoint; `evidence.py` calls through it to date
an event and contains no arithmetic of its own; `main.py` computes every
figure on the page and never calls a model.

So the guarantee is a narrow one, and narrow is what makes it checkable: the
sales data is read, filtered and reduced to a median entirely inside
`main.py`, which has no path to a model, and the modules that do call a model
are never handed those rows. A model's only numeric output in this system is
one ISO date read out of a source document.

`templates/index.html` holds all presentation and the front-end JavaScript.
Nothing in the Python writes HTML, and every string a model produced is written
with `textContent` — nothing takes the `innerHTML` path.

### The lock

Once the Explorer returns its keywords they are fixed, and `parse_plan()`
discards any research direction citing a concept that is not among them —
before a single search runs. The count of discarded directions is reported
rather than hidden.

This is checked in code and not requested in the prompt, because the failure it
prevents is precisely a model seeing A and setting off after B. A rule that
lives only in an instruction is a rule the next model gets to reinterpret.

### The presentation gate

A second model reads each measured finding as a reader would meet it and
answers five fixed questions about how it is **worded**. It is never asked
whether the finding is true.

1. Does every presented event carry an identifiable source?
2. Is causal language used where only sequence is established?
3. Does the result contain a conclusion, prediction, recommendation or probability?
4. Is the observation window stated?
5. Is the claim stronger than the underlying evidence?

A finding fails if 1 or 4 is answered no, or if 2, 3 or 5 is answered yes. It
may be rewritten at most twice, and a rewrite may change only wording — the
date, the source and every figure are out of its reach. Still failing means the
finding is withheld, with its failure categories named and the blocked text not
reproduced.

The gate blocked a real finding on its first live run, and the wording of a
withheld finding never apologises: the test suite scans every reason string for
apologetic language and fails the build if it appears. A withheld finding is
the system working as specified.

---

## The five states

Every research direction ends in exactly one of five states. All five have
occurred against live data.

| State | What it means |
| --- | --- |
| `RESULT` | Dated, sourced, measurable, and it passed the gate |
| `NO_EVIDENCE` | The search ran and the sources held no datable event |
| `RESEARCH_INCOMPLETE` | We could not look: missing key, exhausted quota, timeout, unreachable service, unreachable reviewer |
| `EVENT_OUTSIDE_MEASURABLE_RANGE` | The event is real and dated, but falls before 2017-01-01 |
| `EVIDENCE_FOUND_BUT_WITHHELD` | It did not pass presentation review within two revisions |

**An empty result is a correct result — but only `NO_EVIDENCE` is an empty
result.** It means this search found nothing. A failure to search is not an
empty result: an exhausted quota, an unreachable service, an event outside the
measurable range and a finding blocked by the gate are each a different state
with its own wording. An exhausted quota is a fact about us, not a fact about
the historical record.

One incomplete direction makes the whole analysis incomplete, and that is
stated once at the top rather than only in the margin of the direction it
belongs to.

---

## Data

Two NYC Open Data datasets, read live over Socrata on every question. Nothing
is cached and nothing is stored locally.

| Dataset | Id | Covers |
| --- | --- | --- |
| Citywide Annualized Calendar Sales | `w2pb-icbu` | 2016-01-01 to 2025-12-31 |
| Citywide Rolling Calendar Sales | `usep-8jbt` | 2025-09-01 to 2026-08-31 |

Row counts and date ranges are read from the datasets at request time rather
than hard-coded, and both refresh dates are printed on the page. NYC Open Data
revises these datasets retroactively, which is the publisher correcting the
record rather than a defect.

Measurement uses the median sale price of eligible residential transactions —
nine residential building-class categories, transactions of $100,000 or more.
The floor excludes nominal and zero-consideration transfers, which are recorded
sales but not market prices.

The measurable period begins **2017-01-01**. The annualized dataset begins
2016-01-01 and an event needs a complete twelve-month window behind it, so the
first measurable date is twelve months after the data begins. An event found,
dated and sourced below that floor is reported as real and unmeasurable rather
than quietly dropped.

---

## Scope is a choice, not a ceiling

This version answers questions about residential property sales in the five
boroughs of New York City. One city, one domain, direct API queries rather than
a database, a fixed twelve-month window, one model per job.

None of these are things the framework cannot do. They are things this version
chooses not to do yet.

The value of the project is the framework — **AI explores, evidence verifies,
humans decide** — and that framework is demonstrated as completely by one city
as by fifty. Every hour spent broadening the shell is an hour not spent making
the core flow correct, and every additional feature is another thing that can
break.

Real estate is the first application, not the limit. The same method applies to
any domain that satisfies two conditions: **reliable, traceable historical
records**, and **an outcome that can be measured and linked to a dated event**.
Adding a region changes the dataset, not the application logic — the five
boroughs were enabled without touching the pipeline, which is the evidence for
that claim rather than a promise about it.

We are not showing you the limits of what this can do. We are showing you, as
clearly as possible, how it works.

---

## Known limitations

Stated here deliberately. A reader finds them anyway, and a system about
epistemic honesty cannot be shy about its own.

- **Things without events are invisible to it.** Demographic change, the slow
  erosion of purchasing power, a long interest-rate cycle — any of these may
  matter more than any single rezoning, but none happened on a particular day.
  The system can say "here are events that were recorded, and here is what
  followed". It cannot say "here is everything that mattered".
- **Events are neighbourhood-scale; the data is borough-scale.** All five
  boroughs are available, and every one of them is measured whole: a rezoning
  affecting a few blocks of Gowanus is compared against the median for all of
  Brooklyn. This is a limit on precision, not on coverage. The datasets carry
  `neighborhood` and `nta` columns, so finer granularity is the most valuable
  thing a second version could add.
- **A twelve-month window is a choice, not a finding.** Some events move a
  market in a quarter and some over five years. This version does not
  distinguish them.
- **There is no control group.** The change after an event is not compared
  against the citywide market over the same period, so an event that merely
  coincided with a general rise will show the general rise. Seasonality is
  likewise uncontrolled.
- **The sources are an allowlist, which is a judgement.** A relevant event
  covered only outside those 21 domains will not be found.
- **Nothing is stored between sessions.** No analysis is saved, so research
  paths cannot yet be compared across questions or across models. Recording
  them is the clearest next step, and it is deliberately not in this version.
- **Coverage begins in 2016 and measurement in 2017.** Earlier events — the
  2008 financial crisis among them — can be found and dated but not measured,
  and are reported as such rather than omitted.

---

## Documentation

- [`docs/spec-en.md`](docs/spec-en.md) — the full product specification
- [`docs/START-HERE.md`](docs/START-HERE.md) — entry point for anyone picking up the work

## License

Apache License 2.0 — see [LICENSE](LICENSE).
