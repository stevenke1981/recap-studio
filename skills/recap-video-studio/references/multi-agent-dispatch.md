# 多 agent 派工建議（recap-video-studio 附錄）

適用：片長 ≥ 30 分或章數 ≥ 8。小專案（< 30 分、單人可完成）主控自行跑完，不派工。

## 1. 主控先做（不可派出）
1. S0 立項、風險分級、`project.json`。
2. 定**共用契約**並寫入 `<repo>\projects\<slug>\00_source\brief.md`（約定檔，非契約檔）：
   - 目標、片長、章數、每章字元預算（總預算 × 該弧主線分占比）。
   - story bible 路徑（`01_outline\outline.md`）、風格鎖（圖風前綴、角色外觀描述、旁白語氣）。
   - 硬規則：評論門檻、引文上限、禁用原作影音。
   - 回報格式（見 §4）。
3. 基線：跑 `script_to_shots.py` 與 `tts_batch.py --only ch01` 確認工具鏈通。

## 2. 分波並行
| 波 | 階段 | 並行單位 | 模型 | 各 agent 只動 |
|---|---|---|---|---|
| 1 | S1 場景卡 | 每 agent 一卷／若干章 | Haiku 5.5 | `01_outline\cards\<卷>.md` |
| 1b | S1 合併 | 單一 | Sonnet 5.5 | `01_outline\outline.md`（含 story bible） |
| 2 | S2 撰稿 | 每 agent 一弧（含其章） | Sonnet 5.5 | `02_script\arc<N>.md`；主控合併為 `script.md` |
| 2b | S2 審稿 | 單一或按弧 | Sonnet 5.5 | 只出審稿意見，不改稿 |
| 3 | S3a 提示詞 | 每 agent 數章 | Haiku 5.5 | 回傳 `prompts_<章>.json`，主控合併進 `shots.json` |
| 4 | S4 TTS | 腳本分章 `--only chNN` | 無需模型 | 避免多進程同寫 `manifest.json`：以序列或單次全量為宜 |
| 5 | S3b 生圖 | 見 §3 | Haiku 5.5 管理提示詞與驗收 | `04_assets\images\<id>.*` |
| 6 | S5 合成 | `render.py --jobs N` | 主控 | — |
| 7 | S6 QA | 初審 Haiku 5.5；終審 Sonnet 5.5 | | `08_publish\*` 草稿 |

規則：
- 先實作波，再派 Sonnet 審查優化、Haiku 補文件／說明欄／範例。
- 撰稿 agent 必讀：story bible、風格鎖、前後弧最後一段（接縫）、已定稿之 hook／結尾回扣句。
- 合併 `script.md` 後由主控跑 S2 閘門（字數、引文），再交 H3。
- `shots.json` 整體由主控寫（`script_to_shots.py` 產生並合併）；agent 只交 prompts 片段。

## 3. 生圖並行的限制
- `chatgpt-image-gen`／`browser-image-gen` 依賴**單一已登入 Chrome**（`agent-browser --cdp 9222`）：不得多 agent 同時操作同一帳號與同一瀏覽器；同一時間只一個 agent 出圖。
- 速度屬瓶頸；縮減方式：同場景多段共用一圖（shots.json 允許）、`segment_max_chars` 取大、關鍵圖精做、其餘用圖卡／資訊圖。
- 本機 `stable-diffusion-cpp` 可與雲端出圖並行，但與 TTS／ASR 的 GPU 使用須分時（8 GB VRAM）。
- 生圖失敗（拒絕、逾時）不自動重送；記錄 segment id，改寫提示詞後重試。

## 4. 回報格式（要求各 agent 末訊息）
1. 產出檔案絕對路徑。
2. 完成範圍（章／段 id 區間）。
3. 閘門自檢結果（附指令與輸出摘要）。
4. 與契約／story bible 不一致之處、需主控裁決之事。
5. 未驗證與限制。

## 5. 主控收尾
- 讀各報告 → 整合共用檔（`script.md`、`shots.json`、`sources.csv`、`review_log.md`）→ 跑全套閘門（`qa_check.py`）→ 實測抽看（H4b、H6）→ 回報主人：分工、成果、實測數據、未驗證。
- agent 不得 git add／commit／stash／checkout；commit 與 push 由主控依領域分批，push 須主人明言。
- 用量警示（5 小時額度）時：停派新工、令背景 agent 回報、寫接續筆記（階段、已完成章、下一步指令、環境）。

## 6. 模型選擇理由
- Sonnet 5.5：需連貫與判斷之工作（撰稿、審稿、story bible、風險終審）。
- Haiku 5.5：邊界清楚、量大之工作（場景卡、image_prompt、說明欄初稿、QA 初審）。
- 其中風格一致性靠「風格鎖」與範例句，不靠模型記憶。
