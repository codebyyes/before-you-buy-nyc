# 下一步 — 看完就能動手

寫給接手的框（或明天的我）。背景在 `docs/state-2026-10-11.md`，
這一份只講**接下來做什麼、怎麼做**，不用再重新想一次。

---

## 動作一：Reviewer 閘門（最後一塊）

規格第 9 節 + 修訂 A10。**不花 Tavily，只多一次便宜的模型呼叫。**

### 接在哪

`main.py` 的 `/evidence` 路由，`measure_event()` 算完、`row["state"] =
RESULT` 之前。只有 `RESULT` 需要過閘門，其他四種狀態不用。

### 用哪個模型

```python
explorer.REVIEWER_MODEL   # "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"
```

⚠️ 大小寫跟 Explorer 那個不一樣（前面重複 NVIDIA），不要憑印象打。
已驗證 Nano 夠用，不需要換大模型。

### 它查什麼（五個固定問題，不要加也不要改）

1. Does every presented event carry an identifiable source?
2. Is causal language used where only sequence is established?
3. Does the result contain a conclusion, prediction, recommendation or
   probability?
4. Is the observation window stated?
5. Is the claim stronger than the underlying evidence?

🔴 **它不問「事件是不是真的」，也不問「這個方向值不值得查」。** 開放式複查等於
把實質判斷還給模型，而窄範圍正是為了防這件事（A10 明文）。第五題問的是
「這句話有沒有講得比證據多」，不是「這件事是不是真的」。

### 已驗證的行為

拿一句故意藏四個違規的歷史陳述（用了 "caused"、做了預測、沒來源、沒寫觀察
期間）給它，它回 `FAIL` 然後 `1 2 3 4`。四個字，沒有多話。**對一個閘門來說
那是正確行為**，不要因為「回答太簡短」就去改提示詞。

解析時要容忍 `PASS` / `FAIL` 前後的空白和大小寫，失敗編號可能用空白或逗號分隔。

### 退回機制

最多**兩次**。退回的時候，Explorer **只能用已經取得的證據**改寫 ——
不准重新搜尋、不准補事件、不准換日期。兩次之後還是 FAIL：

```
state = explorer.EVIDENCE_FOUND_BUT_WITHHELD
```

**只顯示被擋下的數量和失敗的題號類別，不顯示被擋下的內容。** 把沒過閘門的
東西放出來，等於繞過閘門。

🔴 **文案不能寫成道歉。** 這是閘門正常運作，不是系統故障。一個宣稱因果而
證據只有先後的發現，**本來就該被擋**。801 糾正過 108 一次，不要再犯。
措辭往「審查沒通過，所以不呈現」寫，不要往「很抱歉無法提供」寫。

### 失敗處理

Reviewer 呼叫本身失敗（逾時、額度、連不上）**不是** withheld，是
`RESEARCH_INCOMPLETE` —— 我們沒審成，不是審過不給。

### 測試

`test_explorer.py` 的方式照抄：stub `explorer.chat`，離線驗
`PASS` / `FAIL 1 2 3 4` / 亂回 / 呼叫失敗 四條路徑，不花半毛錢。
加一條掃描：withheld 的文案裡不准出現 "sorry"、"unfortunately"、"unable"。

---

## 動作二：重驗改過的 `DATE_PROMPT`

`evidence.py` 的 `DATE_PROMPT` 在 10/11 加了三條規則（主題對不上、必須是
發生過的事、文件自己的日期不算），**還沒經過原版那種測試**。

測例至少要包含那個真實踩到的案子：

```
關鍵字：Brooklyn downtown luxury condo oversupply 2021-2022
來源  ：一份 AG 的申報 PDF，檔名含 as-of-august-1-2010，內容是曼哈頓華爾街 40 號
期望  ：found: false
```

以及一條**必須還活著**的：聯準會的新聞稿網址 `monetary20200315b.htm`
→ 日期 2020-03-15 要抽得出來。那是 URL 推日期的正當用法，新規則不能把它殺掉。

---

## 動作三（交件前，別拖到最後）

| | |
|---|---|
| A 區 15 條修訂貼進規格書 | `spec-amendments-2026-10-09.md`，**已寫完，不要重寫** |
| README | 收窄「空結果是正確結果」、重算 Gowanus、改 COVID 那句 |
| README 新增「已知限制」 | 見下方，802 口述的兩條要寫進去 |
| 三分鐘影片 | 目標 2:45。結構在交接文件 |
| `requirements.txt` | 拿掉已經沒用的 `tavily-python`，從 `pip freeze` 釘版本 |

### README 的「已知限制」要寫哪兩條

這兩條是 10/11 凌晨跟 802 談出來的，**自己先講比被評審問出來好**：

1. **沒有事件的事情看不見。** 人口結構變化、購買力長期侵蝕、利率大循環 ——
   這些可能比任何一次 rezoning 影響更大，但它們不是某一天發生的，所以這套
   系統抓不到。系統能說的是「以下是當年被記錄下來的事，以及之後發生了什麼」，
   **不是**「以下是所有重要的事」。
2. **事件是社區級的，資料是行政區級的。** Gowanus 的重劃拿整個布魯克林的
   中位數在量。這在交接文件裡早就誠實記了，而且外部 AI 一眼就看到，
   所以一定要主動寫出來。

---

## 不要在交件前做的事

- 不要降到 neighborhood 粒度（資料集有 `neighborhood`、`nta` 欄位，V2 最值得
  做的方向，但現在動會來不及）
- 不要加季節性對照組
- 不要加第二個 borough
- 其餘見 `state-2026-10-11.md` 最後一節
