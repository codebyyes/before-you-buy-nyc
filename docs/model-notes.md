# What we know about the model, and how we know it

Recorded 2026-10-11, 23:00. Written because the system does not save its own
analyses, so every run we do by hand is a record that exists only if someone
writes it down.

Read this before concluding anything about Nemotron's capability. The short
version: **the evidence does not support "the model reasons poorly", and it
does support two specific, reproducible behaviours.** Treating those as the
same thing is how we would end up writing a submission that violates this
project's own rule about claims outrunning evidence.

---

## Settled

### Question shape drives reasoning depth more than anything else

Two questions, same evening, same borough, same model, same prompts:

| Question | Keywords | Paths |
| --- | --- | --- |
| "Does a hurricane hitting Florida affect home prices in the Bronx?" | 2 | **All one step.** `hurricane Florida -> Hurricane Irma landfall September 2017`, and four more like it |
| "Does extreme weather elsewhere in the country affect Bronx home prices?" | 3 | **All three steps with mechanisms.** `migration -> Puerto Rican evacuees -> NYC shelter announcement` |

The sharper statement, and the one to keep: **what drives the depth is how
much semantic distance the question leaves open.** Give the model a bridge and
it walks the bridge; leave the gap and it builds one.

"Extreme weather elsewhere affects Bronx prices" already contains the leap —
the reader made it. So two of those three-step paths are elaboration rather
than reasoning: `extreme weather -> Hurricane Harvey -> the declaration about
Hurricane Harvey` names an instance and then an official act about that
instance. It looks like a chain and is mostly specification.

"More people are wearing black; does that have anything to do with home
prices?" supplies no link at all. Clothing to protest is a real semantic jump
and nobody handed it over.

One qualification, because the rule is not absolute: inside the bridged
question the model still named `migration` as a keyword — a concept appearing
nowhere in the question — and built `migration -> Puerto Rican evacuees -> NYC
shelter announcement`. It walked the bridge it was given and put up a second
one beside it. Section 7 of the spec exists to allow exactly that.

**Consequence for anyone evaluating this model: a single question tells you
about that question, not about the model.**

### It does not decline; it names something plausible

Spec section 17 recorded this on 2026-10-08 ("Brooklyn black clothing surge
2022"). It reproduced exactly on 2026-10-11, across a prompt revision:

```
black clothing -> new black-themed retail store opening
  -> Opening of 'Black Dress Code' boutique Williamsburg March 2019
```

No such boutique was found. **Two observations, three days apart, different
prompt versions.** This is the one behaviour that currently meets the bar for
a stable finding.

It is also the behaviour the architecture already answers: a fabricated event
finds no source, so it never reaches the reader as a historical claim. This is
worth showing rather than hiding — it is the live demonstration of "the AI may
explore freely, but it may not assert freely".

### The gate blocks real findings, repeatedly

Three live blocks are now on record: Amazon HQ2 (question 5, claim stronger
than evidence), and on 2026-10-11 the California wildfires direction (question
3, a conclusion or prediction), rewritten twice and withheld.

---

## Suspected, not established

### The dating step may be rejecting good sources over a guessed month

The explorer composes a query from memory, and that query often contains a
date it guessed. `sources_block()` labels the whole query `SEARCH TERM:`, and
`DATE_PROMPT` rule one says a source from **a different period** than the
search term asked for returns `found: false`. So a guess is handed downstream
as a requirement.

Four observations, all pointing the same way:

| Query | Date in it | Outcome |
| --- | --- | --- |
| `...Hurricane Harvey August 25 2017` | correct | found |
| `...Gowanus rezoning approved December 2021` | actual date is 2021-11-23 | nothing |
| `...Puerto Rican evacuees November 2017` | guessed | nothing |
| `...Hurricane Maria October 2017` | guessed | nothing |

The Gowanus rezoning is real, and the model found and quoted it correctly on
2026-10-08 when reading sources rather than recalling them.

One competing explanation is ruled out: `esd.ny.gov`, where the 2026-10-08
source was found, **is** in `TRUSTED` in `evidence.py`. The allowlist did not
shut that page out.

**Counter-evidence, 2026-10-12.** Manhattan, "do immigrant protests make home
prices higher". One direction was `home prices -> Federal Reserve emergency
rate cut -> 2020-03-15`, searched with that date — **which is correct**, and
`federalreserve.gov` is in the allowlist. It returned `NO_EVIDENCE` anyway.

So a guessed month is not sufficient to explain the misses: here is a correct
date that found nothing. That run also missed four of six directions, a higher
rate than any run before it. Something else is going on in the search or
dating step that none of the current theories covers.

This direction is also the acceptance case fixed in advance by spec section 17
(the Fed press-release URL `monetary20200315b.htm` must yield 2020-03-15). It
failed here at the search or dating step rather than at the URL-reading step
the acceptance case was written about, so it is not the same test — but it is
close enough to be worth saying out loud rather than filing quietly.

**The mechanism is confirmed in code. The model's actual behaviour is not
observed, because the build container cannot reach Nebius or Tavily.** Do not
change the rule on this alone. It would be a change we equally cannot verify.

This has the same shape as the five bugs already recorded in `spec-en.md`: a
step obeying a constraint nobody told it was a guess.

---

---

## A layout finding, not a model finding

802, 2026-10-12: "it just keeps pulling keywords out of my question."

He is right about what he sees, and the keywords are literal **by design** —
spec section 11 makes them the reader's checkpoint, written the way a person
says them out loud. The leaps live in the paths, and in that same run one of
them went `home prices -> Federal Reserve emergency rate cut -> 2020-03-15`,
which nobody asked about.

But the complaint lands somewhere real. The keywords get a box each, at full
width, above everything — the most prominent element on the page is the least
interesting thing the model produced. The paths, which are where the thinking
actually is, sit in small text under each record.

This is a layout problem, not a model problem, and it is a V2 item. Worth
noting that the keyword tray already took four attempts to get right; the
question this raises is not how it looks but what it is ranked above.

---

## Not known, and what it would take

| Question | Why we cannot answer it | Minimum test |
| --- | --- | --- |
| How much varies run to run? | Every observation is n=1 | Ask one identical question three times and compare |
| Did the period rule kill Gowanus? | No network from the build container | One `DATE_PROMPT` call with a source whose month differs from the query's. Needs a machine that can reach Nebius |
| How often is an extraction reply unusable? | No instrumentation existed until 2026-10-11 | Watch for `RESEARCH_INCOMPLETE` marked `failed_at: extract` in live runs |
| Is Nemotron better or worse than alternatives? | Never compared | Out of scope for this submission. Say nothing about it |

---

## How to talk about this in the submission

Spec section 17's model evaluation is itself a deliverable — the rules make
the feedback section eligible for the Most Valuable Feedback award. Two things
follow:

1. Report the two settled behaviours and the two platform findings (silent
   empty responses from a small `max_tokens` on a reasoning model; model
   identifiers that differ in capitalisation from the catalogue). All four are
   measured and useful to the platform.
2. Do not write "the model's reasoning is insufficient". We have evidence
   against it, and a system built to refuse conclusions that outrun their
   evidence cannot be described in a document that does exactly that.
