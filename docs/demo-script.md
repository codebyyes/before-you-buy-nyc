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
- 🔴 **Do not leave the page while it is researching.** The evidence request
  runs 60 to 120 seconds and a backgrounded tab on an iPad has its request
  killed. It happened on 2026-10-13: every record came back at
  `AWAITING EVIDENCE` with "the request did not reach the server". The page
  handles it correctly, but it is not what you want on film.
- **No music with a copyright, no third party logos** beyond what the page
  itself shows.
- The on screen text can be English only. The narration is English.

## What not to claim in the video

Nothing in this script says the system is right, or that the gate cannot be
passed, or that an event caused a price to move. It took three readings to
get the written materials to that standard. The video is the most watched
thing we produce, so it holds to it too.

---

# 中文對照（給 802 對畫面用，不進影片）

影片裡只有英文。這一份是讓你知道每一句在講什麼，好挑對截圖。

---

**鏡頭 1 · 0:00–0:18 — 問題**
畫面：頁首，標題 + 那行金色標語

> 你去問任何一個 AI 你的房子明年值多少，它都會回答你。**那就是問題。**
> 一個沒人查得了的肯定答案，正是每個人會照著做的那一個。
> Before You Buy NYC 反過來做。**AI 可以看。但它不可以下結論。**

---

**鏡頭 2 · 0:18–0:42 — 官方資料，程式算的**
畫面：Staten Island 的類別表格 → 五年圖表 → **最下面那幾行資料集說明**

> 選一個紐約市行政區。這裡每一個數字都是 Python 從城市自己的成交紀錄算出來的，
> 即時，在頁面載入的那一刻。按官方類別的中位價。成交筆數。五年的季度中位數。
> 這一頁會印出自己的資料集名稱、更新日期和套用的篩選條件，**所以你可以自己查。**

🔴 資料集那幾行停兩秒。那一格證明數字是可追溯的。

---

**鏡頭 3 · 0:42–0:56 — 那個問題**
畫面：問題框「Will home prices in Staten Island go up next year?」

> 現在換買家真正會問的問題。明年會不會漲。
> **這套系統不會回答這個。看它做了什麼。**

---

**鏡頭 4 · 0:56–1:08 — 鎖**
畫面：五個關鍵字的方框

> 第一個模型找出這個問題在問哪些概念，然後設定研究方向。
> 那些概念接著被鎖在程式裡。**任何從別的地方出發的方向，在任何搜尋發生之前就被丟掉。**

---

**鏡頭 5 · 1:08–1:40 — 閘門擋下它** 🔴 **整支片的核心**
畫面：記錄 2，「Finding withheld by presentation review」標籤 + 路徑 + 下面的理由

> 這是第二個模型的工作。它讀每一筆發現，檢查**措辭**，從不檢查真假。
> 這一筆被擋下來了。理由是它自己的話：**一個結論、預測、建議或機率。**
> 它被退回去重寫。兩次。還是沒過，所以不顯示。
> **第一個 AI 往預測的方向飄。第二個把它攔下來。**

🔴 把那句 `a conclusion, prediction, recommendation or probability` 放大。
整個產品的主張濃縮成一行，而且是它自己發生的。

---

**鏡頭 6 · 1:40–2:08 — 過得了的長這樣**
畫面：記錄 5，事件 / 日期 / 日期依據 / ag.ny.gov 來源 / 前後中位價表格

> 這是過得了的。一個真實事件。紐約州驅逐令到期。
> 日期，對照它出處的那句話確認過。一個你點得進去的政府來源。
> 以及事件前後十二個月的中位成交價，從官方資料算出來。
> **不是它造成了什麼。是它之後發生了什麼。**

---

**鏡頭 7 · 2:08–2:32 — 模型**
畫面：Research complete 結論框，**兩個模型 ID 和 Nebius Token Factory 都印在上面**

> 兩個 NVIDIA Nemotron 模型，都在 Nebius Token Factory 上。
> Nemotron 3 Super 負責探索。Nemotron 3 Nano 負責審查。
> **兩個都拿不到成交資料，這一頁上沒有任何數字是模型產出的。**
> 五個方向。一個量到了。兩個查無。兩個被擋下。**每一個都顯示出來。**

🔴 這一格就是滿足「展示 Token Factory 和 Nemotron 用在哪」那條規則的地方。
**不要把模型 ID 裁掉。**

---

**鏡頭 8 · 2:32–2:50 — 收尾**
畫面：回到頁首，或一張只有那三個詞的卡

> 住宅是我們證明它的地方，不是我們想做的東西。
> 這套方法只跟任何一個領域要兩件事。**可追溯的官方紀錄，
> 以及一個能對有日期的事件去測量的結果。**
> AI explores. Evidence verifies. Humans decide.

---

## 錄之前（會毀掉一整天的兩件事）

1. **先把網站叫醒。** 15 分鐘沒人用會睡，第一次載入等約 50 秒。
2. **先跑一次那題再開錄。** 冷開機直接錄，跑出來全空就白錄了。

## 影片裡不准出現的宣稱

這份稿子沒有說系統是對的、沒有說閘門擋得住全部、沒有說事件造成了價格變動。
書面文件花了三輪外部閱讀才守到這條線。**影片是最多人看的東西，所以它也守。**
