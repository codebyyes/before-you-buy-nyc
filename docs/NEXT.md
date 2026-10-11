# 下一步 — 看完就能動手

寫給接手的框（或明天的我）。背景在 `docs/state-2026-10-11.md`，
這一份只講**接下來做什麼、怎麼做**，不用再重新想一次。

---

## ✅ 動作一完成：Reviewer 閘門（2026-10-11）

`explorer.py` 的 `REVIEWER_PROMPT` / `review()` / `withheld_reason()`，
接在 `main.py` 的 `/evidence` 路由，`measure_event()` 之後、`RESULT` 之前。
只有要變成 `RESULT` 的才過閘門，其餘四種狀態不經過。

- 五個固定問題，**不准加第六個、不准改成開放式複查**
- 只用 Nano（`REVIEWER_MODEL`，大小寫跟 Explorer 不同）
- 最多退回兩次。退回時 Explorer **只能改措辭** —— 日期、來源、數字都是
  程式和證據產生的，改寫碰不到
- 兩次還是 FAIL → `EVIDENCE_FOUND_BUT_WITHHELD`，顯示**數量和失敗類別**，
  不顯示被擋下的內容
- 🔴 **Reviewer 自己呼叫失敗不是 withheld，是 `RESEARCH_INCOMPLETE`** ——
  沒審成跟審過不給是兩件事
- 🔴 **文案不道歉。** `test_explorer.py` 有一條掃 sorry / unfortunately /
  unable / apolog / regret / fail，任何一個出現就不過

五種狀態現在在同一頁上都看得到（本地 harness 已驗）。

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
