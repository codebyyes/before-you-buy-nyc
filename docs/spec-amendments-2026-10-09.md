# Specification amendments — 2026-10-09

Drafted by 108. Adjudicated by 801 (`reply-to-agent.md`). Paste the English
blocks into the specification; the Chinese line above each one says what it is
and where it goes.

**Base version.** The sweep in A12 was performed against the specification text
as exported on 2026-09-26 (the `.pages` file). If sections 14, 15 or 16 have
changed since — section 16 was rewritten on 10/08 — the sweep must be repeated
against the current artifact before A12 is closed.

---

## A1 — 新增總則，放在第 10 節開頭（證據規則那一節）

> ### Never state a system condition as a fact about the world
>
> When the system does not know something, it says that it does not know. It
> never converts its own limits into a statement about the historical record.
>
> A search that did not complete, a date that could not be confirmed, a period
> the data does not cover, a finding that did not pass review — none of these
> are evidence that nothing happened. "We found nothing" and "we could not
> look" are different results, and they are never displayed the same way.
>
> This is not a philosophical position. It is a constraint on the system's
> states, enumerated in the section that follows.

---

## A2 — 新增，緊接在 A1 之後：五種狀態

> ### The five states a research direction can end in
>
> Every research direction ends in exactly one of five states. Each is
> displayed differently, and no state is ever displayed as another.
>
> **`RESULT`** — Research completed. A sourced, dated event was found, the
> price movement was calculated by program logic from official data, and the
> finding passed presentation review.
>
> **`NO_EVIDENCE`** — Research completed. No qualifying evidence was found in
> the sources searched. This is a valid research result and is kept, because it
> records that the system looked in a direction and the record did not support
> it. It states that *this search* found nothing. It does not state that the
> historical record contains nothing.
>
> **`RESEARCH_INCOMPLETE`** — The research could not be completed: a search
> service failed, a quota was exhausted, a request timed out. The system does
> not know. This must never be displayed as `NO_EVIDENCE`. The wording is
> *"Research could not be completed"*, not *"no evidence was found"*.
>
> **`EVENT_OUTSIDE_MEASURABLE_RANGE`** — A real, sourced, dated event was
> found, but its date falls outside the period this system's data can measure.
> The historical boundary in section 14 places the earliest eligible event in
> January 2017, because a complete twelve-month pre-event window must exist in
> the dataset.
>
> The event, its date, its date basis and its source are displayed, together
> with the reason it could not be measured. Displaying this as `NO_EVIDENCE`
> would be false: the historical record is not silent, our data does not reach
> it. A question about what followed a financial crisis will surface September
> 2008 — real, documented, and among the most relevant housing events there is.
> Answering "no relevant historical evidence was found" would be a lie about
> the world in order to hide a limit of ours.
>
> **`EVIDENCE_FOUND_BUT_WITHHELD`** — Evidence was found, but the finding did
> not pass presentation review within the permitted revisions (section 9).
>
> **This is the presentation gate operating correctly. It is not a system
> failure.** A finding that claimed causation where the evidence established
> only sequence *should* be blocked. The number of withheld findings and the
> category of failure are displayed; the withheld content is not, because
> showing output that failed the gate would be a way around the gate.
>
> #### Roll-up
>
> States do not stay local to the direction they belong to. If any direction in
> an analysis ends in `RESEARCH_INCOMPLETE`, **the analysis as a whole is
> incomplete**, and that is stated once at the top of the result rather than
> only beside the affected direction.
>
> An analysis that is partly unknown is never presented as a complete analysis
> that happens to contain an empty row.

---

## A3 — 取代第 10 節的 "Result volume" 整段

> **Result volume.** Every finding that passes the presentation gate is
> displayed. The system does not select among findings and does not cap their
> number.
>
> The cap was removed because a selection step cannot be audited unless the
> specification says which component performs it, at what point in the chain,
> and by what visible rule — and this specification never said. An unspecified
> selector at an unspecified point is exactly the kind of invisible judgement
> the rest of the design removes.
>
> It would also almost never apply. One event is confirmed per research
> direction, and the explorer produces as many directions as it judges a
> question to warrant — five to seven in testing — so a question yields a
> handful of cases rather than a list needing to be trimmed. A rule that
> almost never fires is still a rule that has to be specified, justified and
> maintained.

**不要**把這一段寫成防偏差措施。管線順序是：挑關鍵字 → 找事件 → 抽日期 →
程式算漲跌 → Reviewer，所以選擇發生在數字存在之前或之後，規格沒寫。寫成
「我們防止 AI 挑對自己有利的」會讓讀者以為我們在防一個已經證實的問題，而那
沒有被證實 —— 任何一邊都沒有。

---

## A4 — 新增，放在第 14 節 "Eligible residential transactions" 之前

> ### What exclusions are for
>
> A record is excluded because it is not a transaction in which someone
> acquired a place to live. **It is never excluded because its price is
> extreme.**
>
> Every exclusion in this section follows from that single test: nominal and
> zero-consideration transfers are not purchases; entire rental apartment
> buildings are not homes; parking spaces, storage units and vacant land are
> not dwellings. Any exclusion added in future must be justified the same way.

---

## A5 — 新增，接在 A4 之後

> ### No upper price threshold
>
> There is none, and none is to be added.
>
> The price basis is a median, and a median is already insensitive to extreme
> values: one very large sale moves it by a single position among thousands.
> Trimming the top of the distribution would discard valid sales of real homes
> in order to solve a problem the median has already solved.
>
> It would also introduce the judgement "above this price it does not count",
> which is the kind of invisible decision this system exists to avoid. The
> exclusion that applies at the top of the market is by category — categories
> 07, 08 and 14 are whole buildings, not homes — and follows from the test in
> the preceding subsection, not from price.

---

## A6 — 第 14 節，明確寫出邊界

> **Threshold boundary.** The filter is `sale_price >= 100000`. A sale recorded
> at exactly $100,000 is kept. The rule reads "below $100,000 is excluded", and
> below means below.

這一條存在的理由是它曾經漂移過：同一份資料用 `>` 和 `>=` 跑出的 Brooklyn 季度
中位數差 0 到 2,575 美元、筆數差 1 到 6 筆（每季有 1 到 8 筆正好十萬的成交）。
差異很小，但它讓兩次執行對不起來，而可重現性是第 16 節的要求。

---

## A7 — 取代第 14 節關於 nominal consideration 的那句，並成為使用者看得到的文字

> ### Why the low-value exclusion exists, and what it costs
>
> The datasets carry no arm's-length flag. Transfers between family members,
> transfers into trusts or LLCs, and gifts appear in the data in the same shape
> as sales and cannot be identified one by one. They cluster at the bottom of
> the price range, many recorded at $0 or $1. Excluding the range below
> $100,000 removes most of them.
>
> **It also removes genuine low-priced sales** — a house in poor condition, a
> cheap co-op share. That is the cost of the approximation, not a side benefit
> of it, and the cost falls entirely on one end of the distribution, so every
> median it produces is slightly higher than one computed without it.
>
> The number of eligible transactions the threshold removes, and their share of
> the total, are displayed alongside the filter, so that the reader can judge
> the trade-off instead of taking it on trust.
>
> **Whether $100,000 is the right place for that line is open.** It is higher
> than the $10,000 used in academic work on New York residential transactions,
> and higher than the $25,000 statutory threshold of the New York City Real
> Property Transfer Tax. The question is to be settled by measuring how far the
> medians move as the line moves, and the measurement published with the
> answer.

⚠️ 不要在這裡引用那份 NYC City Planning FEIS 的 $100,000 排除理由。108 查了
兩次搜尋加一次文件抓取，查不到原文；拿不到網址和頁碼之前，按第 10 節「沒有
來源不能呈現」，不能引用。$25,000 那條是查證過的（NYC DOF 2018 年 RPTT 統計
報告）。

---

## A8 — 第 14 節 "Transaction counts" 整段改寫

> ### What a transaction count counts
>
> Every median is displayed with the number of transactions that entered that
> median — **not** the number of transactions that occurred in the period. The
> two differ by whatever the price threshold and the eligibility rules removed.
>
> The count's purpose is to describe the sample behind the figure beside it,
> which is why it is filtered identically to that figure. A count filtered
> differently from its median would not describe it.
>
> This distinction matters wherever the count is used to qualify a price
> movement. **A count filtered for price analysis does not measure market
> activity and must not be described as though it did.** Where the text wishes
> to say that trading slowed, it must say so from a figure that measures
> trading.
>
> The system does not label a sample reliable or unreliable. It shows the count,
> states what the count includes, and leaves the judgement to the reader.

**連帶要改的：** 介面表頭 `Sales` → `Sales in median`；來源說明區塊加一行說明
筆數是篩選後的；以及 README 裡那句用筆數描述「成交量掉五分之一」的敘述 ——
那句話要麼改成價格樣本的說法，要麼換一個真正測量成交量的數字。

---

## A9 — 第 8 節，用這一句取代原本的解釋段落

> The explorer sets its own question, and may then only look for answers inside
> the question it set.
>
> The freedom is in framing the question; the constraint is in answering it.
> Without the constraint the freedom would be worthless, because the explorer
> could retroactively change the question to whichever one happened to have an
> answer.

出自 802，比原本那一整段清楚。

---

## A10 — 第 9 節，釐清 Reviewer 問什麼

> The reviewer asks a fixed set of questions about how a finding is presented:
>
> 1. Does every presented event carry an identifiable source?
> 2. Is causal language used where only sequence is established?
> 3. Does the result contain a conclusion, prediction, recommendation or
>    probability?
> 4. Is the observation window stated?
> 5. Is the claim stronger than the underlying evidence?
>
> It does not ask the explorer whether it is sure, and it does not reopen
> whether the event is real or whether the direction was worth taking. An
> open-ended re-check would return substantive judgement to a model, which is
> precisely what the narrow scope exists to prevent. The fifth question asks
> whether a sentence claims more than its evidence carries — not whether the
> underlying event is true.
>
> Observed behaviour matches this scope: given a statement containing four
> deliberate violations, the reviewer returned `FAIL` followed by `1 2 3 4`.
> Four tokens, no elaboration. For a gate, that is correct behaviour.

---

## A11 — 第 17 節末尾，記錄 `kind` 實驗的處置

> The `kind` field experiment described above is deferred to a version after
> V1. The architecture already prevents a fabricated event from reaching the
> user — it finds no source and therefore no result — so the cost of the
> failure mode is wasted search quota rather than a false claim. Building the
> interface takes priority over reducing a cost that does not reach the reader.
>
> The acceptance criterion is fixed in advance and carries over unchanged: the
> direction `Brooklyn protest attire black clothing 2020` must survive. It was
> the most valuable output of the evaluation — a model connecting a trivial
> surface observation to a documented period of unrest. If a revision
> suppresses it, the revision has over-corrected, however much the fabrication
> rate improves.

---

## A15 — 第 9 節開頭補一段：這道閘門為什麼存在（108 新增，802 口述的專案史）

第 9 節目前解釋的是「為什麼審查範圍要窄」，沒有記錄**為什麼會有審查者**。那段
歷史只存在 802 的記憶裡（2026-10-09 凌晨口述），現在寫下來：

> ### Why there is a second model at all
>
> The first substantive response this project received from a language model
> was that it could not be built. The objection was specific: a model asked to
> research a question will talk itself into an answer — it reasons toward
> something plausible and then presents the reasoning as a finding.
>
> That objection is the reason this section exists. The design did not add a
> reviewer for general safety; it added a gate against one named failure mode,
> identified before any code was written. The explorer is still allowed to
> reason toward whatever it likes, because that is where its value is. What it
> is not allowed to do is be the one who decides that its reasoning has become
> a result.
>
> The objection was correct, and it was later measured: given a question with
> no real event behind it, the explorer produced plausible event names for
> things that never happened (section 17). The architecture was already shaped
> for that behaviour because a critic had described it in advance.

**802 的評語值得一併記下：「我覺得他還是有他的用處。」** 那個模型的價值不在於
它說對了（它說做不成，結果做成了），而在於它**精確命名了失敗模式**。這跟這個
產品對 Explorer 的要求是同一件事 —— 不要求它說對，只要求它指出一個方向。

⚠️ 要不要在規格裡點名是哪個模型，由 802 決定。上面的寫法沒有點名。點名更誠實，
但這份規格會隨投稿公開，而比賽是 Nebius × NVIDIA 辦的 —— 這是觀感問題，不是
事實問題，所以交給他判斷。

---

## A12 — 清掉規格書裡編造的示意數字

801 提出第 14 節那組，108 照要求掃過全文，**另外找到三處**。

### A12-1 — 第 14 節，Transaction counts 的示意數字（801 提出）

目前是：

```
Pre-event:  median $800,000 — 342 sales
Post-event: median $850,000 — 17 sales
Change: +6.25%
```

三個數字都是編的，但格式跟真實測量結果一模一樣。**802 本人已經把它跟真正的
COVID 測試記混過一次。**

處置：換成真實測量值。最接近那一節要講的事的是聯準會 2020-03-15 緊急降息那組
（價格只動 2.94%，筆數掉兩成，市場其實停擺了）—— 但現有那組是**未加九類過濾**
的早期管線測試。**正確做法是重跑一次過濾版再寫進規格**，不要加註標籤了事。

### A12-2 — 第 14 節，不完整窗口的示意百分比（108 新增）

```
March 2018 → following 12 months: +6.2%
Recent — March 2026 → March 2026 to September 2026 (6 months elapsed): +3.1%
```

同樣是編造的百分比，同樣是測量結果的格式。而且這一組更危險：它示範的正是
「不完整窗口」那條規則，而那條規則的重點就是不要讓六個月的數字被讀成十二個月
的數字。**用假數字示範一條防止誤讀的規則，本身就是在示範那個誤讀。**

處置：換成真值，或改寫成不帶數字的格式說明（`+X.X%` / `YYYY-MM`）。

### A12-3 — 第 14 節，交易量的估計值（108 新增）

```
These account for roughly 87,000 of the approximately 100,000 annual transactions.
...rental apartment buildings (categories 07, 08 and 14 — roughly 4,100
transactions a year)
```

這兩個數字用了 "roughly" 和 "approximately"，所以沒有偽裝成精確測量 —— 但也
沒有說它們是怎麼來的。**它們可以被直接算出來**（九類／三類在年度資料集裡的
年均筆數），所以沒有理由留著估計值。

處置：用實際查詢的結果取代，並註明算的是哪個期間。

### A12-5 — 第 6 節，圖表規則裡的示意百分比（108 新增）

```
Figures are presented as statements of fact ("+4.2% versus the same quarter
last year") rather than as characterisations ("an upward trend").
```

`+4.2%` 在引號裡、明顯是格式範例，風險比前面幾處低 —— 但它仍然是測量值的形狀，
而且第 6 節講的正是「數字要陳述事實」。照 A12-4 的規則改成 `+X.X%`。

### A12-4 — 全文規則

> Any figure that appears in this specification in the shape of a measurement
> is a measurement. Illustrative figures are written in a form that cannot be
> mistaken for one (`$X`, `+X.X%`, `N sales`) or are not used.

理由：這份規格的讀者包含接手的 AI 和評審。一個長得像測量值的編造數字，會被
下一個人當成基準去比對 —— 而那正是這個產品在防的事情，發生在這個產品自己的
文件裡。

---

## A13 — 第 21 節同樣要收窄「空結果是正確結果」（108 新增，優先於 README）

第 21 節（寫給接手者看的那節）目前寫著：

> An empty result is a correct result. If no evidence is found, the system says
> so and shows nothing. Do not add fallback explanations, AI-generated
> summaries, or "best guesses" to fill the space.

**C1 原本只針對 README，但這句話也在規格第 21 節裡，而第 21 節是接手的人和 AI
最先讀的一節。** 它現在會教下一個接手者把五種狀態全部壓成一個空結果 —— 正好
是 A1 和 A2 要禁止的事。改成：

> A genuine empty result is a correct result. Where research completed and the
> record did not support a direction, the system says so and shows nothing. Do
> not add fallback explanations, AI-generated summaries, or "best guesses" to
> fill the space.
>
> But an empty result is only correct when it is true. A search that failed, a
> quota that ran out, an event outside the measurable range, and a finding the
> gate withheld are **not** empty results, and displaying them as one states a
> falsehood about the historical record. See the five states in section 10.

---

## A14 — 第 13 節的證據鏈漏掉事前窗口（108 新增）

第 13 節寫：

> AI finds event → event source displayed → official price data → program
> calculates the movement **over the following 12 months** → reviewer checks
> presentation → result shown → human judgment

但第 14 節的測量規則是**事件後 12 個月對照事件前 12 個月**。這條摘要只提了
後半段，讀起來像是只算事後。改成：

> ...→ program calculates the movement across the twelve months before and
> after the event date → ...

小地方，但第 13 節那條鏈是整份規格最常被引用的一句，而且接手的人會照它實作。

---

## 不在 A 區但連帶要改的

| 位置 | 改什麼 | 依據 |
|---|---|---|
| README | `An empty result is a correct result.` 收窄到只涵蓋 `NO_EVIDENCE` | C1 |
| README | COVID 那句用筆數描述成交量的敘述 | A8 |
| README | Gowanus 的 +6.79% 用 `>=` 重算 | D1 |
| README | 新增「已知限制」一節：殘餘幻覺面是「真實事件 + 捏造的理由」，第 9 節刻意不擋 | C3 |
| 第 15 / 16 節 | 802 已於 10/08 改寫（不儲存，可重現性由畫面承擔）—— A12 的掃描需要在改寫後的版本上重做一次 | — |
