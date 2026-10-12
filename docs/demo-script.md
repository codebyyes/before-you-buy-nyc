# Demo video script

Three minutes or shorter, public on YouTube, and it has to show the project
working **and** how Nebius Token Factory and NVIDIA Nemotron were used.

374 words of narration. At a normal text-to-speech pace that is about 2:30,
leaving room for pauses between shots. Do not add filler to reach three
minutes; shorter is better than padded.

---

## For the text-to-speech

The narration below is written to be read aloud by a machine, so:

- **No em dashes, no slashes, no code identifiers.** A model id like
  `nvidia/nemotron-3-super-120b-a12b` will be mangled. It is **shown on
  screen** instead, and spoken in plain English.
- Short sentences. Full stops where a human would breathe.
- Numbers are written the way they should sound.

Read it exactly as written. If a line sounds wrong in the voice you pick,
change it to something shorter rather than longer.

---

## Shots

Timings are a guide, not a cut list. **Almost every screenshot you need is in
the Staten Island run from 2026-10-12, 18:02 to 18:05.**

---

### 1 · The problem — 0:00 to 0:18

**On screen:** the site header. Title, the line *AI explores · Evidence
verifies · Humans decide*.

> Ask any AI what your home will be worth next year, and it will tell you.
> That is the problem. A confident answer nobody can check is the one
> everybody acts on. Before You Buy NYC is built the other way round. The AI
> may look. It may not conclude.

---

### 2 · Official data, computed — 0:18 to 0:42

**On screen:** Step 1 confirmed for Staten Island. The property class table,
then scroll to the five year chart, then the dataset lines at the foot of the
column.

> Pick a New York City borough. Every figure here is computed in Python from
> the city's own sales records, live, at the moment the page loads. Median
> price by official property class. Transaction counts. Five years of
> quarterly medians. The page prints its own dataset names, refresh dates and
> the exact filter applied, so you can check it yourself.

🔴 **Hold on the dataset lines for two seconds.** That is the shot that
proves the numbers are traceable.

---

### 3 · The question — 0:42 to 0:56

**On screen:** the question box reading *Will home prices in Staten Island go
up next year?*

> Now the question a buyer actually asks. Will prices go up next year. This
> system will not answer that. Watch what it does instead.

---

### 4 · The lock — 0:56 to 1:08

**On screen:** the keyword tray, five keywords, the line under it.

> The first model names the concepts the question is about, and sets research
> directions. Those concepts are then locked in code. Any direction that sets
> out from anything else is discarded before a single search runs.

---

### 5 · The gate blocks it — 1:08 to 1:40 🔴 **the most important shot**

**On screen:** Record 2 of 5. The badge reading *Finding withheld by
presentation review*, the path, and the reason text underneath.

> Here is the second model's job. It reads each finding and checks how it is
> worded, never whether it is true. This one was blocked. The reason, in its
> own words: a conclusion, prediction, recommendation or probability. It was
> sent back and rewritten. Twice. It still did not pass, so it is not shown.
> The first AI drifted toward predicting. The second one stopped it.

🔴 **Zoom in on the sentence** *Presentation review found a conclusion,
prediction, recommendation or probability.* This is the whole product in one
line, and it happened on its own.

---

### 6 · What does get through — 1:40 to 2:08

**On screen:** Record 5 of 5. Event, date, date basis, the ag.ny.gov source,
and the before and after table with the change.

> And here is what does get through. A real event. The expiration of New York
> State's eviction moratorium. The date, confirmed against the sentence it
> came from. A government source you can click. And the median sale price in
> the twelve months before and after, computed from official rows. Not what
> caused it. What followed it.

---

### 7 · The models — 2:08 to 2:32

**On screen:** the *Research complete* summary box. Both model ids and the
words *Nebius Token Factory* are printed there. Let them be readable.

> Two NVIDIA Nemotron models, both on Nebius Token Factory. Nemotron 3 Super
> explores. Nemotron 3 Nano reviews. Neither one receives the sales data, and
> no figure on this page was produced by a model. Five directions. One
> measured. Two found nothing. Two withheld. Every one of them shown.

🔴 This shot is what satisfies the rule about showing where Token Factory and
Nemotron were used. **Do not crop the model ids out.**

---

### 8 · Close — 2:32 to 2:50

**On screen:** back to the header, or a plain card with the three words.

> Housing is where we proved it, not what we set out to build. The method
> needs two things from any field. Official records, and an outcome you can
> measure against a dated event. AI explores. Evidence verifies. Humans
> decide.

---

## Before you record

- **Wake the site first.** The free tier sleeps after fifteen idle minutes and
  the first load takes about fifty seconds. Open it, let it load, then start.
- **Run the question once before filming.** If you film a cold run and it
  comes back all empty, you have filmed a blank page.
- **No music with a copyright, no third party logos** beyond what the page
  itself shows.
- The on screen text can be English only. The narration is English.

## What not to claim in the video

Nothing in this script says the system is right, or that the gate cannot be
passed, or that an event caused a price to move. It took three readings to
get the written materials to that standard. The video is the most watched
thing we produce, so it holds to it too.
