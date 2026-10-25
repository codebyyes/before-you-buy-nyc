# Demo video script

Rewritten 2026-10-25. Three minutes or shorter, public on YouTube, and it has
to show the project working **and** how Nebius Token Factory and NVIDIA
Nemotron were used.

**480 words. Whether that fits depends entirely on the voice, not on the
script.** At 160 words a minute it runs 2:58. At 175 it runs 2:43. At a slow
145 it runs 3:17, which is over.

🔴 **So do this before cutting anything.** Pick the 剪映 voice, have it read
shot 1 alone (53 words), and time it. 53 words in 20 seconds or less means
160 wpm or faster and the whole script fits as written. Slower than that, cut
from the list below, in order, and stop as soon as it fits.

**Cut list, in order.** Each of these can go without damaging the point of
its shot. Running totals are at 160 wpm.

| # | Shot | Line to delete | Words | Script becomes |
|---|---|---|---|---|
| 1 | 6 | *The route you are reading is a commitment it made before it knew what it would find.* | 17 | 458 · 2:52 |
| 2 | 5 | *Two completed runs found different events and different figures, both sourced.* | 11 | 447 · 2:48 |
| 3 | 7 | *Nobody tells it what to say.* | 6 | 441 · 2:45 |
| 4 | 1 | *That is the problem.* | 4 | 437 · 2:44 |
| 5 | 2 | *Pick a New York City borough.* | 6 | 431 · 2:42 |

Cut 1 is first because the sentence restates what the two before it already
established. **Do not cut shot 8's "Not what caused it. What followed it."**
That is the product's own sentence and it is 8 words.

The timings on each shot below are computed at 160 wpm, not measured.
Re-fix them from the real audio. Do not pad to reach three minutes; shorter
is better than stretched.

**What changed from the first version.** Three things 802 asked for, and they
are now the spine of the video rather than details inside it:

- **Nobody chooses the keywords.** The model reads the question and decides
  what it is about. The viewer never types them.
- **They are not the same twice.** Eight runs of one question, a stable core
  and a moving edge. This is the thing most likely to be mistaken for a bug,
  so it is said out loud and framed as what it is.
- 🔴 **The route is the product.** Before it searches, the model declares the
  path from one of its own keywords to what it expects to find, in arrows, in
  the reader's language — the prompt says outright that paths are *for the
  reader* (`explorer.py:152`), and it is told not to filter out unusual ones
  (`:159`). That is not a chain of thought. A chain of thought is a model's
  unverifiable account of its own insides. A path is a **commitment**: stated
  before the search, locked to the keywords, reviewed for wording, and then
  left standing next to whatever it actually ran into. **This is what 802
  built the system to observe, and it was missing from the first two drafts
  of this script.**
- **We cannot promise the model never invents an event.** That is stated
  plainly, and then what the architecture does about it is shown rather than
  claimed.
- **It does not refuse you, and it does not conclude for you.** You may ask
  it anything, including next year. What comes back is what already happened,
  sourced. Saying "the system will not answer that" made it sound broken;
  802 corrected it on 10-25.
- **The second model is a mirror, not a judge.** It emits a verdict and
  nothing else. The first model reads its own sentence back and rewrites it.
  See the note under shot 7 before writing any of this into the English
  submission materials.

---

## For the text-to-speech

- **No em dashes, no slashes, no code identifiers.** A model id like
  `nvidia/nemotron-3-super-120b-a12b` will be mangled. It is **shown on
  screen** and spoken in plain English.
- Short sentences. Full stops where a person would breathe.
- Read it exactly as written. If a line sounds wrong in the voice you pick,
  make it shorter, never longer.

---

## Shots

### 1 · The problem — 0:00 to 0:20 (53 words)

**On screen:** the site header. Title, and the line *AI explores · Evidence
verifies · Humans decide*.

> Ask any AI what your home will be worth next year, and it will tell you.
> That is the problem. A confident answer nobody can check is the one
> everybody acts on. The AI here may look. But what it hands you is not a
> conclusion. It is information you can check yourself.

---

### 2 · Official data, computed — 0:20 to 0:31 (30 words)

**On screen:** Step 1 confirmed. The property class table, then the five year
chart, then the dataset lines at the foot of the column.

> Pick a New York City borough. Every figure here is computed in Python from
> the city's own sales records, live. The page prints its dataset names,
> refresh dates and filters.

🔴 Hold two seconds on the dataset lines. That is the shot that proves the
numbers are traceable.

---

### 3 · The question — 0:31 to 0:44 (34 words)

**On screen:** the question box reading *Will home prices in Staten Island go
up next year?*

> Now the question a buyer actually asks. Ask it anything, even this. It will
> not refuse you, and it will not predict for you. It answers with what has
> already happened, every finding sourced.

---

### 4 · Nobody chose these — 0:44 to 0:56 (33 words)

**On screen:** the keyword tray. Let the five boxes be readable.

> These five concepts are not search terms anybody typed. The model read the
> question and decided what it is about, and how many. Everything below
> starts from one of these and nothing else.

---

### 5 · And they are different every time 🔴 **what 802 asked for** — 0:56 to 1:18 (59 words)

**On screen:** two keyword trays from different runs, side by side or cut
one to the other. **You already have these screenshots** — 10-12, 10-13 and
25-10 each produced a different set.

> Ask again tomorrow and the list is not the same. We have asked this one
> eight times. Interest rates, zoning and infrastructure come back every
> time. The rest moves. Two completed runs found different events and
> different figures, both sourced. That is not a fault. Asking again is
> closer to consulting a second adviser than to checking an answer.

---

### 6 · The route it declared before it looked 🔴 **the core of the project** — 1:18 to 1:48 (80 words)

**On screen:** a record's *LOOKED FOR* block. 🔴 **Hold on the PATH line and
let the arrows be readable.** That line is the shot this whole project exists
to show: not a chain of thought, a declared route.

🔴 **The path spoken in the narration must be one the system actually
produced, and the keyword it starts from must be visible in shot 4.** The
ferry route starts from `infrastructure projects`, so shot 4 needs a keyword
tray containing that chip — two of 802's three Staten Island trays do. Swap
in a different real path if the footage calls for it, and change the
narration with it.

⚠️ Until 2026-10-25 this line read *Black clothing, to protest movements, to
market instability. That is a real one.* **That was not a real run**: it is
the illustrative example inside `explorer.py`'s own prompt, and it is the one
that contradicts the prompt's rule about not ending a path at a trend (see
`docs/model-notes.md`). Narrating it as a run output would have been a claim
the repository disproves.

> Watch this line. Before it searches anything, the model writes down the
> route it means to take, from one of its own keywords to what it expects to
> find. Infrastructure projects, to the Staten Island Ferry, to a terminal
> upgrade. That is one from a real run. Then the keywords are locked and the
> search runs. If something
> more interesting appears halfway through, it cannot go after it. The route
> you are reading is a commitment it made before it knew what it would find.

---

### 7 · Can it make things up 🔴 **the honest centre** — 1:48 to 2:24 (95 words)

**On screen:** Record 1, the badge reading *Finding withheld by presentation
review*, and the reason text underneath.

> Can the model invent an event? We cannot promise it never does. We have
> watched it name a boutique that does not appear to exist. But an invented
> event finds no source, and without a source nothing is published. It is
> never listed as a historical event at all. Then every finding goes to a
> second model. It answers only pass or fail, and which line was crossed.
> The first model gets its own sentence back, and rewrites it itself. Nobody
> tells it what to say. This one carried a prediction. Rewritten
> twice. Still withheld.

🔴 Zoom on the reason line: *a conclusion, prediction, recommendation or
probability.* That is the whole product in one sentence, and it happened on
its own.

---

### 8 · What gets through — 2:24 to 2:38 (38 words)

**On screen:** the record that reached `RESULT`. Event, date, date basis, the
clickable source, and the before and after table.

> Here is what gets through. A real event, the date confirmed against
> the sentence it came from, a source you can click, and the median price
> twelve months before and after. Not what caused it. What followed it.

---

### 9 · Close — 2:38 to 2:58 (53 words)

**On screen:** the *Research complete* summary box — both model ids and the
words *Nebius Token Factory* are printed there — then the header.

> Two NVIDIA Nemotron models on Nebius Token Factory. One explores, one
> reviews, neither sees the sales data. Housing is where we proved this, not
> what we set out to build. It needs two things from any field: official
> records, and an outcome measurable against a dated event.
> AI explores. Evidence verifies. Humans decide.

🔴 This shot is what satisfies the rule about showing where Token Factory and
Nemotron were used. **Do not crop the model ids out.**

---

## Before you record

- **Wake the site first.** It sleeps after fifteen idle minutes and the first
  load takes about fifty seconds.
- **Run the question once before filming.** A cold run that comes back empty
  is a blank page on film.
- 🔴 **Do not leave the page while it is researching.** The evidence request
  runs sixty to ninety seconds and a backgrounded tab on an iPad has its
  request killed. It happened on 10-13.
- **If a run ends with "the model's response was not valid JSON", re-run.**
  It is roughly one run in ten, the page handles it correctly, and it is not
  a state worth explaining on camera.
- No copyrighted music, no third party logos beyond what the page shows.

## What this script does not claim

It does not say the system is right, that the gate cannot be passed, that an
event caused a price to move, or that the model never invents anything. The
written materials took three outside readings to reach that standard. The
video is the most watched thing here, so it holds to it too.

---

# 中文對照（給 802 對畫面用，不進影片）

影片裡只有英文。這一份讓你知道每一句在講什麼，好挑對截圖。

---

**鏡頭 1 · 0:00–0:20 — 問題**
畫面：頁首，標題 + 金色標語

> 你去問任何一個 AI 你的房子明年值多少，它都會回答你。**那就是問題。**
> 一個沒人查得了的肯定答案，正是每個人會照著做的那一個。
> **AI 可以看。但它給你的不是結論，是你可以自己去查的資訊。**

---

**鏡頭 2 · 0:20–0:31 — 官方資料，程式算的**
畫面：類別表格 → 五年圖表 → **最下面的資料集說明**（停兩秒）

> 選一個紐約市行政區。這裡每個數字都是 Python 從城市自己的成交紀錄即時算出來的。
> 按官方類別的中位價。成交筆數。五年的季度。
> 這一頁印出自己的資料集名稱、更新日期和篩選條件。

---

**鏡頭 3 · 0:31–0:44 — 那個問題**
畫面：問題框

> 現在換買家真正會問的問題。明年會不會漲。
> **你可以問任何問題，連這一個都可以問。它不會拒絕你，也不會預測你。**
> 它回給你的是**已經發生過的事**，而每一筆放出來的都有來源。

---

**鏡頭 4 · 0:44–0:56 — 這些不是你選的**
畫面：五個關鍵字方框

> 這五個概念**不是任何人打進去的搜尋詞**。是模型讀了問題，自己決定它在問什麼，
> 連要幾個都是它決定的。下面每一筆都從這裡面出發，**不能從別的地方出發。**

---

**鏡頭 5 · 0:56–1:18 — 而且每次都不一樣** 🔴 **你要的那一段**
畫面：兩次不同執行的關鍵字方框，並排或接著切
**截圖你已經有了**——10/12、10/13、10/25 三次各是不同的一組

> 明天再問同一題，清單就不一樣。我們問過八次。
> 利率、分區、基礎建設每次都在。其他的會變。
> 兩次跑完的執行**找到不同的事件、給出不同的數字**，兩個都有來源，兩個都用同樣的方式測量。
> **這不是故障。再問一次比較像多找一位顧問，不是去核對答案。**

---

**鏡頭 6 · 1:18–1:48 — 它在看之前就宣告的路線** 🔴 **專案的核心**
畫面：一筆記錄的 LOOKED FOR 區塊，**停在 PATH 那一行，讓箭頭看得清楚**

> **看這一行。** 在它搜尋任何東西之前，模型先寫下它打算走的路線——
> 從它自己的某一個關鍵字，走到它預期會找到的東西。
> **基礎建設 → 史泰登島渡輪 → 航廈改建。那是真的跑出來的一條。**
> 然後關鍵字被鎖上，搜尋才跑。半路上出現更有意思的東西，它也不能追過去。
> **所以你讀到的那條路線，是它在還不知道會找到什麼之前就做出的承諾。**

---

**鏡頭 7 · 1:48–2:24 — 它會不會亂編** 🔴 **最誠實的一段**
畫面：被擋下那一筆，徽章 + 下面的理由

> 模型會不會編出一個事件？**我們不能保證它永遠不會。**
> 我們親眼看過它說出一家查不到的精品店。
> 但編出來的事件找不到來源，**而沒有來源的東西不會被發表**，
> **它根本不會被列為一個歷史事件。**
> 然後每一筆發現都會送給第二個模型，它只回答通過或不通過，以及越過了哪一條。
> **第一個模型拿回自己寫的那句話，必須自己重寫。沒有人告訴它該怎麼寫。**
> 這一筆因為夾帶預測被擋下。重寫兩次。還是沒放出來。

🔴 **第二隻 AI 到底是什麼**（802 的設計原意，2026-10-25 口述，影片用這一版）

當初設的理由是**怕第一支 AI 太會自圓其說**——不是怕它說謊，是怕它把順序講成
因果、把證據講得比它承載的多。而對策不是去抓它，是**讓它自己意識到自己在哪個
方向**。

程式真的是這樣跑的（`explorer.py` 544–589）：第二個模型的全部輸出只有
`PASS`，或者 `FAIL` 加幾個數字——四個 token，不改字、不重寫、不給理由。
退回去的時候，收到東西的是**第一支 AI 自己**（第 570 行用 `EXPLORER_MODEL`），
它拿到的是「被退的是第幾條」加上「它自己寫的那句話，原封不動」，附帶指示的最後
一句是 *You are changing how this is said, nothing else.*

**所以主角是第一支 AI，不是審查員。** 審查員是舉鏡子的那隻手。五個問題裡
第 2、5 條（順序不准講成因果、話不准比證據大）就是衝著自圓其說來的，另外三條
是結構性的。

⚠️ **822 在 10/25 把主角寫反過一次**，寫成「審查員去看它看得見的東西」。
從程式讀回去猜設計原意，猜錯的方向剛好是最常見的那個（AI 互相監督）。
寫英文報告的時候不要再滑回去。

💾 **另一條理由，影片砍掉但留著給英文說明報告用**：模型去審另一個模型的真假，
自己也沒有通往現實的特權，那是猜兩次；第一支 AI 鐵了心往幻覺跑，疊幾層模型
都是浪費。真假是由**來源要求**檢查的，那是一道機械的門，不是一個判斷。
這條跟上面那條不衝突——一條講為什麼不查真假，一條講它到底在做什麼。
影片只塞得下一條，報告塞得下兩條。

⚠️ 802 問對了，原本那句寫成「讀過每一筆發現」太寬。
**只有有事件、有日期、算得出價格的那幾筆才送審**；查無證據、超出範圍、
算不出來的，在閘門之前就跳出去了。規格是刻意這樣設計的——沒有找到東西的
記錄沒有東西可以講過頭。

🔴 把那句 `a conclusion, prediction, recommendation or probability` 放大。

---

**鏡頭 8 · 2:24–2:38 — 過得了的長這樣**
畫面：跑出 RESULT 那一筆（事件 / 日期 / 日期依據 / 來源 / 前後表格）

> 這是過得了的。一個真實事件，日期對照它出處的那句話確認過，
> 一個你點得進去的政府來源，以及事件前後十二個月的中位成交價，從官方資料算出來。
> **不是它造成了什麼。是它之後發生了什麼。**

---

**鏡頭 9 · 2:38–2:58 — 收尾**
畫面：Research complete 結論框（**兩個模型 ID + Nebius Token Factory 都在上面**）→ 回頁首

> 兩個 NVIDIA Nemotron 模型，在 Nebius Token Factory 上。一個探索，一個審查。
> **兩個都拿不到成交資料。**
> 住宅是我們證明它的地方，不是我們想做的東西。
> 它只跟任何領域要兩件事：**可追溯的官方紀錄，以及一個能對有日期的事件去測量的結果。**
> AI explores. Evidence verifies. Humans decide.

🔴 **不要把模型 ID 裁掉**——那一格就是滿足比賽規則的地方。

---

## 錄之前

1. **先把網站叫醒**（15 分鐘沒人用會睡，第一次載入等約 50 秒）
2. **先跑一次再開錄**
3. 🔴 **跑的時候不要離開頁面**（會被 iPad 凍結，10/13 發生過）
4. **跑出「不是有效的 JSON」就重跑**——約十次一次，畫面處理得正確，不值得在鏡頭上解釋
5. 不要有版權音樂、不要有第三方商標

## 這份稿子沒有宣稱的事

沒有說系統是對的、沒有說閘門擋得住全部、沒有說事件造成了價格變動、
**也沒有說模型永遠不會亂編**。

書面文件花了三輪外部閱讀才守到這條線。影片是最多人看的東西，所以它也守。
