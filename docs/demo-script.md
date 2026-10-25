# Demo video script

Rewritten 2026-10-25. Three minutes or shorter, public on YouTube, and it has
to show the project working **and** how Nebius Token Factory and NVIDIA
Nemotron were used.

412 words of narration. Under three minutes at any sane pace: 2:50 at a
slow 145 words a minute, 2:30 at a brisk 165. Do not
pad to reach three minutes; shorter is better than stretched.

**What changed from the first version.** Three things 802 asked for, and they
are now the spine of the video rather than details inside it:

- **Nobody chooses the keywords.** The model reads the question and decides
  what it is about. The viewer never types them.
- **They are not the same twice.** Eight runs of one question, a stable core
  and a moving edge. This is the thing most likely to be mistaken for a bug,
  so it is said out loud and framed as what it is.
- **We cannot promise the model never invents an event.** That is stated
  plainly, and then what the architecture does about it is shown rather than
  claimed.

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

### 1 · The problem — 0:00 to 0:18

**On screen:** the site header. Title, and the line *AI explores · Evidence
verifies · Humans decide*.

> Ask any AI what your home will be worth next year, and it will tell you.
> That is the problem. A confident answer nobody can check is the one
> everybody acts on. This is built the other way round. The AI may look. It
> may not conclude.

---

### 2 · Official data, computed — 0:18 to 0:38

**On screen:** Step 1 confirmed. The property class table, then the five year
chart, then the dataset lines at the foot of the column.

> Pick a New York City borough. Every figure here is computed in Python from
> the city's own sales records, live. The page prints its dataset names,
> refresh dates and filters, so you can check it yourself.

🔴 Hold two seconds on the dataset lines. That is the shot that proves the
numbers are traceable.

---

### 3 · The question — 0:38 to 0:48

**On screen:** the question box reading *Will home prices in Staten Island go
up next year?*

> Now the question a buyer actually asks. The system will not answer it.
> Watch what it does instead.

---

### 4 · Nobody chose these — 0:48 to 1:04

**On screen:** the keyword tray. Let the five boxes be readable.

> These five concepts are not search terms anybody typed. The model read the
> question and decided what it is about, and how many. Everything below
> starts from one of these and from nothing else.

---

### 5 · And they are different every time — 1:04 to 1:30 🔴 **new, and the one 802 wants**

**On screen:** two keyword trays from different runs, side by side or cut
one to the other. **You already have these screenshots** — 10-12, 10-13 and
25-10 each produced a different set.

> Ask again tomorrow and the list is not the same. We have asked this one
> eight times. Interest rates, zoning and infrastructure come back every
> time. The rest moves. Two completed runs found different events and
> different figures, both sourced. That is not a fault. Asking again is
> closer to consulting a second adviser than to checking an answer.

---

### 6 · It has to follow its own keywords — 1:30 to 1:48

**On screen:** a record's *LOOKED FOR* block — the FROM chips and the PATH,
with the searched line underneath.

> Once named, the concepts are fixed in code. The model must search from its
> own list. If something more interesting appears halfway through, it cannot
> go after it. Anything setting out from elsewhere is discarded before a
> single search runs.

---

### 7 · Can it make things up — 1:48 to 2:14 🔴 **the honest centre**

**On screen:** Record 1, the badge reading *Finding withheld by presentation
review*, and the reason text underneath.

> Can the model invent an event? We cannot promise it never does. We have
> watched it name a boutique that does not appear to exist. What we can show
> is what happens next. An invented event finds no source, so it is never
> published. And every finding on its way to being shown goes to a second
> model first, which asks five fixed questions about how it is worded, never
> whether it is true. This one carried a prediction. Rewritten twice. Still
> withheld.

🔴 Zoom on the reason line: *a conclusion, prediction, recommendation or
probability.* That is the whole product in one sentence, and it happened on
its own.

---

### 8 · What does get through — 2:14 to 2:34

**On screen:** the record that reached `RESULT`. Event, date, date basis, the
clickable source, and the before and after table.

> Here is what does get through. A real event, the date confirmed against
> the sentence it came from, a government source you can click, and the
> median price twelve months before and after. Not what caused it. What
> followed it.

---

### 9 · Close — 2:34 to 2:50

**On screen:** the *Research complete* summary box — both model ids and the
words *Nebius Token Factory* are printed there — then the header.

> Two NVIDIA Nemotron models on Nebius Token Factory. One explores, one
> reviews, and neither receives the sales data. Housing is where we proved
> this, not what we set out to build. The method needs two things from any
> field: official records, and an outcome measurable against a dated event.
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

**鏡頭 1 · 0:00–0:18 — 問題**
畫面：頁首，標題 + 金色標語

> 你去問任何一個 AI 你的房子明年值多少，它都會回答你。**那就是問題。**
> 一個沒人查得了的肯定答案，正是每個人會照著做的那一個。
> 這個產品反過來做。**AI 可以看。但它不可以下結論。**

---

**鏡頭 2 · 0:18–0:38 — 官方資料，程式算的**
畫面：類別表格 → 五年圖表 → **最下面的資料集說明**（停兩秒）

> 選一個紐約市行政區。這裡每個數字都是 Python 從城市自己的成交紀錄即時算出來的。
> 按官方類別的中位價。成交筆數。五年的季度。
> 這一頁印出自己的資料集名稱、更新日期和篩選條件，**所以你可以自己查。**

---

**鏡頭 3 · 0:38–0:48 — 那個問題**
畫面：問題框

> 現在換買家真正會問的問題。明年會不會漲。
> **這套系統不會回答這個。看它做了什麼。**

---

**鏡頭 4 · 0:48–1:04 — 這些不是你選的**
畫面：五個關鍵字方框

> 這五個概念**不是任何人打進去的搜尋詞**。是模型讀了問題，自己決定它在問什麼，
> 連要幾個都是它決定的。下面每一筆都從這裡面出發，**不能從別的地方出發。**

---

**鏡頭 5 · 1:04–1:30 — 而且每次都不一樣** 🔴 **你要的那一段**
畫面：兩次不同執行的關鍵字方框，並排或接著切
**截圖你已經有了**——10/12、10/13、10/25 三次各是不同的一組

> 明天再問同一題，清單就不一樣。我們問過八次。
> 利率、分區、基礎建設每次都在。其他的會變。
> 兩次跑完的執行**找到不同的事件、給出不同的數字**，兩個都有來源，兩個都用同樣的方式測量。
> **這不是故障。再問一次比較像多找一位顧問，不是去核對答案。**

---

**鏡頭 6 · 1:30–1:48 — 它必須照自己的關鍵字走**
畫面：一筆記錄的 LOOKED FOR 區塊（FROM 方框 + PATH + 搜尋字串）

> 一旦命名，這些概念就被鎖在程式裡。模型只能從自己這份清單出發。
> **半路上出現更有意思的東西，它也不能追過去。**
> 從別的地方出發的方向，在任何搜尋發生之前就被丟掉。

---

**鏡頭 7 · 1:48–2:14 — 它會不會亂編** 🔴 **最誠實的一段**
畫面：被擋下那一筆，徽章 + 下面的理由

> 模型會不會編出一個事件？**我們不能保證它永遠不會。**
> 我們親眼看過它說出一家查不到的精品店。
> **我們能給你看的是接下來發生什麼。** 編出來的事件找不到來源，所以永遠不會被發表。
> 而且沒有東西會沒被讀過就到你面前：**每一筆即將被展示的發現**，都會先送給第二個模型，
> 它用**五個固定問題**檢查措辭，從不檢查事情是不是真的。
> 這一筆因為夾帶預測被擋下。重寫兩次。還是沒放出來。

⚠️ 802 問對了，原本那句寫成「讀過每一筆發現」太寬。
**只有有事件、有日期、算得出價格的那幾筆才送審**；查無證據、超出範圍、
算不出來的，在閘門之前就跳出去了。規格是刻意這樣設計的——沒有找到東西的
記錄沒有東西可以講過頭。

🔴 把那句 `a conclusion, prediction, recommendation or probability` 放大。

---

**鏡頭 8 · 2:14–2:34 — 過得了的長這樣**
畫面：跑出 RESULT 那一筆（事件 / 日期 / 日期依據 / 來源 / 前後表格）

> 這是過得了的。一個真實事件，日期對照它出處的那句話確認過，
> 一個你點得進去的政府來源，以及事件前後十二個月的中位成交價，從官方資料算出來。
> **不是它造成了什麼。是它之後發生了什麼。**

---

**鏡頭 9 · 2:34–2:50 — 收尾**
畫面：Research complete 結論框（**兩個模型 ID + Nebius Token Factory 都在上面**）→ 回頁首

> 兩個 NVIDIA Nemotron 模型，在 Nebius Token Factory 上。一個探索，一個審查。
> **兩個都拿不到成交資料。**
> 住宅是我們證明它的地方，不是我們想做的東西。
> 這套方法只跟任何領域要兩件事：**可追溯的官方紀錄，以及一個能對有日期的事件去測量的結果。**
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
