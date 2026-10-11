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

Naming a category of event ("hurricane Florida") invites enumeration, and
enumeration is arguably the correct response to it. Giving an abstract
category ("extreme weather elsewhere") forces a chain.

In the second run the model named `migration` as a keyword — a concept that
appears nowhere in the question — and then built a path from Hurricane Maria
through Puerto Rican displacement to New York City housing. That is the
behaviour section 7 of the spec exists to allow.

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

**The mechanism is confirmed in code. The model's actual behaviour is not
observed, because the build container cannot reach Nebius or Tavily.** Do not
change the rule on this alone. It would be a change we equally cannot verify.

This has the same shape as the five bugs already recorded in `spec-en.md`: a
step obeying a constraint nobody told it was a guess.

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
