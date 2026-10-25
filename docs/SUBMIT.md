# Devpost submission — the paste sheet

Everything the form asks for, one field at a time, ready to copy. Written
2026-10-26. **Submissions close 2026-10-30, 10:00 PT — that is 2026-10-31,
01:00 in Taipei.**

⚠️ **This list is built from the hackathon rules and from how Devpost forms
usually look. Nobody on this project can reach the logged-in form.** If the
real form has a field that is not below, it is not covered here — screenshot
it and it will be answered.

---

## Before you start

| | |
| --- | --- |
| Live site | https://before-you-buy-nyc.onrender.com |
| Repository | https://github.com/codebyyes/before-you-buy-nyc |
| Video | https://www.youtube.com/watch?v=qBgl_KVVWsg |
| Track | **Best Apps and Agents** |

🔴 **Wake the live site before submitting** and leave the tab open. It sleeps
after fifteen idle minutes on the free tier and the first load takes about
fifty seconds. A judge clicking into a cold start sees a blank page.

---

## 1 · Project name

```
Before You Buy NYC
```

## 2 · Elevator pitch

The one-line summary under the title. Devpost caps this near 200 characters;
this is 192.

```
An AI that researches New York housing questions and is not allowed to answer them. It finds dated events, measures what followed in the city's own sales records, and shows every route it took.
```

## 3 · Project description

The long one, in Devpost's usual sections: Inspiration / What it does / How we
built it / Challenges we ran into / Accomplishments we're proud of / What we
learned / What's next.

👉 **It is in [`devpost.md`](devpost.md), everything from the heading
`# Project description — paste into Devpost` down to the end of that file.**
Copy the whole thing. It is kept there rather than repeated here so there is
only ever one copy to correct.

Do not paste the lines above that heading — those are working notes, not
submission text.

## 4 · Built With

Devpost wants lowercase hyphenated tags, one per box:

```
python, flask, nvidia-nemotron, nebius-token-factory, tavily,
nyc-open-data, socrata, render, github, javascript, html, css, svg
```

Nothing else belongs here. The only installed dependency is Flask; everything
else in the Python is the standard library, the page loads no external script,
and the chart is hand-written SVG.

## 5 · Try it out links

```
https://before-you-buy-nyc.onrender.com
https://github.com/codebyyes/before-you-buy-nyc
```

## 6 · Video demo link

```
https://www.youtube.com/watch?v=qBgl_KVVWsg
```

⚠️ **Use this `watch?v=` form, not the `youtube.com/shorts/…` one.** They are
the same video. YouTube filed it as a Short because it is vertical and under
three minutes; the watch URL opens it in the ordinary player, which is what
Devpost embeds. Drop any `?si=…` on the end — that is a share-tracking tag.

The video is 2:40 and public. Its closing frame prints both model identifiers
and the words *Nebius Token Factory*, which is what satisfies the rule about
showing where they were used.

## 7 · Track

```
Best Apps and Agents
```

## 8 · Feedback on Nebius and NVIDIA tools

🔴 **This is a submission requirement, not an optional extra.** The rules put
it in the same list as the video and the repository: *"Provide feedback on
Nebius Token Factory, AI Cloud and any NVIDIA tools, models, or technologies
used."* A submission that leaves it blank is incomplete. Completing it also
enters the **Most Valuable Feedback** award ($100 + swag, ten winners), but
that is a bonus on top, not the reason to fill it in.

👉 **The text is in [`devpost.md`](devpost.md) under `## Platform feedback`.**
Two findings, both measured during the build:

1. A reasoning model returns an empty string with no error when `max_tokens`
   is spent on reasoning before the answer begins.
2. The two models' API identifiers differ in capitalisation from the
   catalogue.

## 9 · Pre-existing project?

```
No.
```

Begun after the submission period opened, so no "significant updates" summary
is needed. 802 did not attend an in-person Builders & Brews event, so no city
is selected.

---

## Already done — do not redo

- ✅ Public repository, Apache-2.0 licence, detected by GitHub
- ✅ README with install steps, environment variables and offline checks
- ✅ Working demo URL, all five boroughs enabled
- ✅ Public YouTube video, 2:40, under the three-minute cap
- ✅ Where the NVIDIA models and Token Factory were used — stated in the
  README, in the description, and printed on the page itself at the end of
  every run
- ✅ Platform feedback written

## After the deadline

- 🟢 **Move Render off the free tier before 2026-12-01**, when judging opens.
  On the free tier the site sleeps after fifteen idle minutes, and a judge
  will not wait fifty seconds for a cold start.
- 🟢 Everything in `docs/multi-model.md` and `tools/variance.py`, both of
  which were deliberately left until after submission.
