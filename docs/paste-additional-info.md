# Devpost "Additional info" — every field, ready to paste

Written 2026-10-28. The answers below are written to be true, not to be
flattering: where we did not measure something, they say so. Judges and the
Nemotron team both read this section, and a project whose whole premise is
that a claim must not outrun its evidence cannot answer a feedback form any
other way.

---

## Upload a File
Skip. Not required.

## * Submitter Type
```
Individual
```

## * Organization Name (if applicable)
```
N/A
```

## * Submitter Country of Residence
```
Taiwan
```

## * If you or any team members reside in Canada, indicate the province
```
N/A
```

## * Which track are you submitting your project into?
```
Best Apps and Agents
```

## * Is your project new or existing prior to August 26, 2026?
```
New
```

## If your project is existing, explain how you significantly updated it
Leave blank. The project is new, and this field is not required.

## * URL to your public code repository
```
https://github.com/codebyyes/before-you-buy-nyc
```

## URL to a working demo
```
https://before-you-buy-nyc.onrender.com
```

---

## * Which model(s) did you use, and why did you choose that size/variant?

```
Two, both on Nebius Token Factory.

nvidia/nemotron-3-super-120b-a12b is the Explorer. It reads the user's question, names the concepts the question is about and decides how many it needs, declares a research route from each concept to the kind of dated event it expects to find, and later reads search results to date an event against its own source. That is open-ended associative work and it needed the larger model.

nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B is the Reviewer. It reads a finished finding as a reader would meet it and answers five fixed questions about how it is worded, then emits PASS, or FAIL and the numbers of the questions that failed. Four tokens. That is a narrow, repeated classification job, and 30B is more than enough for it.

The split cost one line of configuration because a single OpenAI-compatible endpoint serves both. With two vendors we would not have bothered, and the review gate — which is the point of the whole project — would probably not exist.
```

---

## * How would you rate Nemotron's output quality for your use case? (1-10)

```
7.

What worked well:

Associative reach. From the keyword "black clothing" it reached the George Floyd protests in New York City, June 2020, with a news source and a quoted date. From "coffee shop openings" it reached a City Council vote on a ground-floor retail zoning amendment, with a Legistar record. Neither of those is on any checklist a human would have written.

Format discipline. Bare JSON on essentially every call, no preamble, no markdown fencing, so the pipeline consumes the output directly.

It sizes its own answer. Told only to decide how many research directions a question warrants and not to pad, it produced seven for a vague question and three for a tightly constrained one. It was never given a number.

Nano is excellent at the narrow job. Given a finding containing four deliberate presentation violations it returned FAIL 1 2 3 4, in four tokens.

Where it fell short:

It does not decline. Asked to name something specific that may not exist, it produces a plausible name rather than stopping. It named a "Black Dress Code boutique, Williamsburg, March 2019" that does not appear to exist, and reproduced the same invention three days later across a prompt revision. Our architecture catches this — no source, no publication — but a model that answered "I cannot name one" would be more useful than one that guesses well.

Reasoning depth tracks the shape of the question more than it tracks capability. Same model, same evening, same borough: a question that already contained the inferential leap produced five one-step directions that were really a list; the same question with the leap removed produced three-step chains with mechanisms. A single prompt tells you about that prompt, not about the model.

What this rating is not: a benchmark. It is a working judgement from roughly twenty live runs, recorded as we went in docs/model-notes.md.
```

---

## * Did you fine-tune, prompt-engineer, or use Nemotron out of the box? What was your approach?

```
Out of the box, prompt-engineered, no fine-tuning and no few-shot examples beyond two illustrative research paths.

The approach was to put as little as possible in the prompt. The rule that matters most in this system — that a research direction may only start from one of the concepts the model itself named — is enforced in code, in parse_plan(), not requested in the instruction. A direction citing anything else is discarded before a single search runs, and the count of discarded ones is shown to the user. A rule that lives only in an instruction is a rule the next model gets to reinterpret.

The finding we would most like to pass on is about prompts, not about Nemotron: a prompt is code that nothing type-checks.

On 2026-10-25 we found our own explorer prompt telling the model never to end a research path at a trend, listing "the market cooled" among its examples, and then, thirty-four lines later, offering "Black clothing -> protest movements -> market instability" as a valid example path. The rule and the illustration contradicted each other and had done so for two weeks.

In the same pass we found that a wording change inside an unrelated refactor had quietly weakened the definition of a path from "the chain of reasoning that led you there" to "the route from those keywords to the event". The model had been faithfully giving us the weaker thing ever since — two-term paths with no reasoning step — and we had been reading it as a model limitation. It was not. Both are recorded with their commits in docs/model-notes.md.

Neither was caught in review, because a prose change inside a large diff is invisible in a way a code change is not.
```

---

## * How did Nemotron's performance compare to other models you've used for similar tasks?

```
We did not run that comparison, and we are not going to imply one.

The architecture makes it cheap to run — the explorer model is a single constant — and the comparison is designed and written up in docs/multi-model.md in the repository. It was deliberately left until after the submission deadline. The premise of this entire project is that a claim must not outrun its evidence, and a comparison we have not run is not evidence.

The one comparison we can report is of kind rather than of quality. Asked the same housing question, a general-purpose assistant returned a confident, well-organised answer citing a study. It turned out to be accurate, but it took two further lookups to establish that. Ours returned a government URL and the exact sentence the date came from, one click from verification. The honest trade is that ours often reads as plainer.
```

---

## * Which Nebius platform capabilities were most valuable to your project and how?

```
To be precise about scope: we used Token Factory serverless inference only. No AI Cloud GPU instances, no deployment of our own, no scaling configuration. We cannot speak to instance types or cluster setup, and would rather say so than guess.

Three things mattered.

One OpenAI-compatible endpoint serving both models. This is the reason the project has two models rather than one. Handing the narrow review job to a smaller, faster model cost one line of configuration instead of a second integration, and that is the difference between the review gate existing and not existing.

No SDK required. We call the endpoint with Python's standard library over plain HTTPS. The whole project has exactly one installed dependency, Flask. A deployment log early on showed an official client library being installed for what amounted to one POST request; we removed it. For a project that has to stay live and unattended through a judging window, every dependency removed is one thing that cannot move underneath a redeploy.

A 120B and a 30B behind the same key and base URL. Swapping the reviewer to test it was a string change.

One reliability note, offered as a fact rather than a complaint: on 2026-10-25 the endpoint returned HTTP 529 "System is overloaded" in the middle of a run. Our system reports that as research that could not be completed rather than as an empty result, so it cost us nothing and it was actually a useful demonstration of that state, but it did happen.
```

---

## * How likely are you to recommend running Nemotron on Nebius to other developers? (1-10)

```
9.

The integration cost was close to zero: an OpenAI-compatible endpoint, no SDK, and two models of very different sizes behind one key. That low cost is the only reason a two-model architecture was worth building inside a hackathon timeframe, and the two-model split is the most interesting thing about the project.

What keeps it off 10 is the silent empty response described in the next answers. We lost real hours to it twice, and both times the API reported success.
```

---

## * How would you rate your experience running Nemotron inference on Nebius compared to previous cloud or local development environments? (1-10)

```
8, with a caveat that makes this an unusual data point: we have no previous environment to compare against.

This project was built entirely from an iPad. One of us cannot read code and has no computer at all; the other is an AI that cannot see the deployed site. There was no local GPU, no local Python, no prior cloud setup. A hosted OpenAI-compatible endpoint was not the convenient choice, it was the only possible one.

So read the 8 as this: a developer with no machine of their own was able to build and ship a live two-model product against Token Factory, from a tablet, and the platform was never the thing standing in the way. That is not a comparison, but it may be worth more to you than one.
```

---

## * What additional features or improvements would have made the Nemotron on Nebius experience more effective?

```
1. A distinct finish reason when the token budget is spent during reasoning.

Nemotron 3 Super reasons before it answers, and the reasoning is billed against the same budget as the answer. A call with max_tokens=20 returned content: "" with finish_reason: "stop" and no error at all; the usage object showed 35 reasoning tokens consumed and 5 remaining. A developer meeting this has no indication of what went wrong — the call succeeded, and the answer is empty. It bit us a second time when the Reviewer was first wired at 256 tokens and came back empty on every single call. A finish reason such as "length_during_reasoning" would have saved both.

2. Separate the reasoning from the answer in the response body.

Our own worst parsing bug came from the same root. The model writes its reasoning as prose before the JSON object, which is expected behaviour; our extractor took the span from the first brace to the last, and a single brace anywhere in that prose broke it. That bug is ours, not yours — but a response that returned reasoning and answer as separate fields would have made it impossible to write.

3. Make the catalogue show the API identifier.

The two models' identifiers follow different capitalisation conventions and neither matches its catalogue display name. client.models.list() is the only reliable source. Showing the exact API string in the catalogue would save every developer that step.

4. A documented way to pin a model version, for a project that has to behave the same way during a judging window weeks after it was submitted.
```

---

## * What do you most hope to see from the Nemotron team next?

```
Characterisation of what varies between runs, and guidance on reproducibility.

Our product's distinguishing feature is that it shows the route the model declared before it searched, rather than only the answer. That makes something visible that most systems hide: ask the same question twice and the model names different concepts and declares different routes. A stable core comes back every time and the edges move.

We think that is interesting rather than broken — it is closer to consulting a second adviser than to re-checking an answer. But we could not establish whether we were watching the model genuinely approach the question differently, or sampling noise wearing a convincing costume. We wrote the experiment to separate them and ran out of time before the deadline.

Documented guidance on what is stable and what is not across identical calls — or simply a reproducibility story — would be worth more to this project than more capability.
```

---

## * Did you use Tavily in your project?
```
Yes
```
Tavily is called live at request time, once per research direction, at advanced
depth against an allowlist of 21 authoritative domains. At default quality the
search returned betting sites and cryptocurrency news for a housing question.

## Builders & Brews - IRL Events City
Leave unselected. 802 did not attend an in-person event.

## * Checkbox — age of majority
Tick it.

## * Checkbox — not an employee of the Promotion Entities
Tick it.

---

## * Which AI tools have you leveraged while working on this project?

```
Claude (Anthropic), through Claude Code, wrote essentially all of the code. One of us is not a programmer and has no computer; the work was done by describing intent, reading back explanations in plain language, testing on an iPad, and sending screenshots back as the only form of verification available. Several of the project's real bugs were caught that way rather than by the AI.

ChatGPT (OpenAI) was used for outside review of the written materials. It caught two claims in our README that the code did not support, both of which were corrected and both of which are now described in the submission.

NVIDIA Nemotron 3 Super and Nemotron 3 Nano, on Nebius Token Factory, are not tools used to build the project — they are the product.

Tavily provides the live search the Explorer runs against.
```

---

## * Describe the level of learning you/your team derived from the project
Pick the highest option offered. A non-programmer shipped a live two-model
application from a tablet.

## * Did you gain AI value that you can use in your career?
```
Yes
```
