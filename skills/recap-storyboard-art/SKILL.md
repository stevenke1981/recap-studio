---
name: recap-storyboard-art
description: 將口播稿轉為分鏡（shots.json）並產出配圖的 Recap Studio 步驟。涵蓋 script.md 切段、共用場景合併、圖像提示詞（全片風格前綴、角色固定外觀、負面提示）、生圖路由（ChatGPT／Gemini 網頁、本機 stable-diffusion-cpp、少量 grok 動態鏡頭）、批量命名與重試、motion 選擇、佔位預覽、素材來源紀錄（sources.csv）與版權／AI 揭露。當使用者提到一口氣看完、解說影片、說書、recap、分鏡、shots.json、配圖、生圖、圖像提示詞、角色一致性、素材來源時使用。
---

> `<repo>` 指本 repo（recap-studio）之 clone 路徑，例如 `D:\recap-studio`。

# recap-storyboard-art：分鏡與配圖

## 用途

把 `02_script/script.md` 轉成 `03_storyboard/shots.json`，為每張圖寫提示詞、生成、存檔，並填好來源欄位與 `00_source/sources.csv`。畫面全為 AI 原創寫實影視風靜態圖，不剪原作畫面、不用原聲。

依據：`<repo>\research\01-yedeng-analysis.md`（靜態圖＋旁白形式）、`02-genre-craft.md`（4–8 秒切換、運鏡幅度、YouTube 揭露與版權檢查點 CP-3／CP-4）、`03-toolchain.md`（工具可用性）、`templates/CONTRACT.md`（欄位與目錄）。

## 輸入／輸出

| 項目 | 路徑（`<P>` = `projects/<slug>/`） |
|---|---|
| 輸入 | `<P>/02_script/script.md`、`<P>/project.json`、`<P>/01_outline/outline.md`（人物表與圖像風格聖經） |
| 輸出 | `<P>/03_storyboard/shots.json`、`<P>/04_assets/images/<segment_id>.png`（1920×1080） |
| 輸出 | `<P>/00_source/sources.csv`（素材來源，必填）、`<P>/00_source/image_gen_log.csv`（生成紀錄，見第 5 節） |

`sources.csv` 與 `image_gen_log.csv` 之欄位皆以 `templates/CONTRACT.md` 為準。

## 步驟

### 1. 產生 shots.json

```
python <repo>\scripts\script_to_shots.py <P>
```

- 參數以 `-h` 為準：`--force` 會覆寫既有 shots.json，預設會合併（文字未變之段保留 image、image_prompt、motion、source、source_ref）。
- 每段預設 `image` 為 `04_assets/images/<segment_id>.png`，`motion` 依序輪替。下列步驟會覆寫這兩項。
- `<!-- image: ... -->` 只套用到其後第一段（該段落首段）。
- 合併僅依文字相同判定：改動旁白後，該段的圖與提示詞會遺失，需重新檢查。

### 2. 合併共用場景

- 同一章內、同一場景（地點、人物組、時間相同）之連續段合併為一組（group），組內每段 `image` 填**同一路徑**。
- 組的檔名以**組內第一段** `segment_id` 命名：`04_assets/images/<第一段 id>.png`。
- 累計時長：段長估算 = `字數 ÷ 270 × 60` 秒（與 script_to_shots 之 `CHARS_PER_MINUTE` 一致）；已有 TTS 時改用 `05_audio/manifest.json` 之 `duration`。
- 換圖間隔依片型（見下表），組內累計超過上限即切新組；場景改變必切。不跨章。
- 只有組內第一段寫 `image_prompt`，其餘段留空。

| 片型 | 換圖間隔（預設值，可依頻道數據調整） |
|---|---|
| 古典志怪／短篇懸疑 | 8–12 秒 |
| 歷史 recap | 10–16 秒 |
| 現代小說／情感 | 6–10 秒 |
| 動作／高潮段 | 4–6 秒 |
| 靜思／回憶段 | 12–20 秒（上限 20 秒，超過則拆組或加字卡） |

依據：02 §2.1 推論為平均 4–8 秒；01 §3 觀察〈武則天〉多為 10–20 秒一圖。以上為本 skill 之設計值。

### 3. 撰寫 image_prompt

每組一則，組成方式（範本與 3 個示例見 `references/prompt-style.md`）：

1. **全片風格前綴**：取自 `01_outline/outline.md` 之「圖像風格聖經」區塊（寫實影視感、光線、色調、畫幅 16:9）。全片一字不改。
2. **角色固定外觀**：只寫本組出場人物，逐字取自 outline 人物表之「外觀固定描述」。不得臨時改髮色、服色、年齡。
3. **場景描述**：依旁白翻譯為視覺（人物動作、構圖、景深、時辰、天氣），不照抄旁白原句，不寫對白。
4. **鏡頭與運鏡提示**：可寫特寫、全景、俯拍等構圖詞，運鏡由 motion 欄位控制，不在提示詞寫「推進鏡頭」。
5. **負面提示**：以句子附於末尾，格式「避免：……」（shots.json 無獨立負面欄位）。

### 4. 生圖

依第 4.1 節路由選工具，一組一圖，產出後依第 5 節存檔。

### 5. 存檔與驗收

- 下載檔複製／改名為 `04_assets/images/<組第一段 id>.png`（不以工具預設檔名留存）。
- 尺寸非 16:9 者以 Pillow 中心裁切或補邊至 1920×1080（Pillow 已裝；可直接 `python -c` 處理，或由主控提供腳本）。
- 驗收：檔案存在、可開啟、非全黑／全白、尺寸正確、畫面無大字或水印（有則重生）。
- 每張在 `image_gen_log.csv` 記一列（欄位：`prompt_id,image,tool,status,attempt,started_at,size,note`，`status` ∈ `ok|retry|failed|placeholder`）。

### 6. 填 source／source_ref

- 組內**每一段**都填相同值：
  - `source`：`ai`（本 skill 之預設）、`screenshot`（預設禁用，見第 8 節）、`original`、`stock`（公版圖像）。
  - `source_ref`：AI 圖填 `<tool>|<log prompt_id>`，例 `chatgpt-image-gen|ch03_g02`；公版圖填出處 URL 並註記「公版」。
- shots.json 之 `source` 與 `source_ref` 應與 sources.csv 一致。

### 7. 寫 00_source/sources.csv

表頭依 CONTRACT（7 欄，不可改順序）：

```
asset_id,type,source,url_or_ref,license,used_in,notes
```

- 每組一列：`asset_id`＝圖檔名；`type`＝`image`；`source`＝`ai|original|stock|screenshot`；`url_or_ref`＝`<tool>|<prompt_id>` 或公版出處 URL；`license`＝AI 圖填 `generated`，公版圖填授權；`used_in`＝組內所有 segment id，以 `;` 分隔。
- `notes` 以 `key=value` 記：`photoreal=yes|no`（寫實人物或事件判為 yes，發布時須勾 AI 揭露）。工具、提示詞、嘗試次數等細節記入 `image_gen_log.csv`。
- 沒有對應列的圖不得進入發布。

## 4.1 生圖路由

| 工具 | 何時用 | 限制與注意 |
|---|---|---|
| `chatgpt-image-gen`／`browser-image-gen`（ChatGPT／Gemini 網頁） | 預設主力，畫質高 | 需使用者已登入之瀏覽器 session；網頁比例非 16:9，須後製裁切；每張下載後驗檔；不得替換使用者 profile。 |
| `stable-diffusion-cpp`（本機） | 離線、無雲端依賴、大量產圖 | 8 GB VRAM：SDXL 與量化 Flux 可跑（依該 skill），Flux q4 約需 6 GB，不得與 TTS 模型同時載入，須分階段。建議 16:9 工作解析度（如 1344×768，推論）再放大裁切。**本次未編譯，未驗證**，首次使用先依該 skill 完成編譯。 |
| `grok-imagine-video`（雲端，需登入） | 只用於少量需要真實動態的鏡頭，每片建議 3–5 段以內（設計值） | 產出為 mp4，與契約 `image`（png）不符：由主控裁定後，以 ffmpeg 抽首幀存為 png，mp4 另存並記入 sources.csv。需登入、720p／10 秒；曾遇後端 500。 |

## 5. 批量化

- 以**章**為一批：先生成 `ch01` 全部組，檢查、記錄，再進下一章。每批建議不超過 12 張（設計值），以免網頁工具限流。
- 命名一律 `<組第一段 id>.png`；prompt_id 格式 `ch{NN}_g{NN}`。
- 失敗重試：
  - 單張最多 3 次（含首次）。
  - 內容政策拒絕：改寫提示詞為中性描述後再試，不得以規避手段繞過。
  - 網頁逾時：先確認是否已生成（下載夾、網頁結果），不得自動重送，以免重複扣額度。
  - 三次皆失敗：以 `make_placeholders.py` 佔位，`status=placeholder`，發布前必須替換。
- 生成紀錄與 sources.csv 須同批更新，不得事後補填。

## 6. Motion 選擇規則

shots.json 之 `motion` ∈ `zoom_in | zoom_out | pan_left | pan_right | static`。

| 情境 | motion |
|---|---|
| 人物特寫、臉部情緒、關鍵道具 | `zoom_in` |
| 場景全景、群像、移動中的景 | `pan_left` 或 `pan_right`（依下一組的視線方向交替） |
| 情緒收束（章末、結局、餘韻） | `zoom_out` |
| 字卡、資料頁、古畫原圖 | `static` |

- 縮放幅度 1.00 → 最多 1.15；位移速度低於約 2%／秒（避免暈眩）。
- 相鄰兩段 motion 不得相同；兩段 pan 方向不得相同。script_to_shots 之輪替不保證此條件，須人工檢查覆寫。

## 7. 預覽（缺圖佔位）

```
python <repo>\scripts\make_placeholders.py <P>
```

- 以 `-h` 為準（`--force` 重產佔位、`--chars` 設定字數顯示）。該腳本可能仍在開發，與本節不符時以 `-h` 為準。
- 不得以 `python -I` 執行：隔離模式看不到使用者安裝的 Pillow，會報 `No module named 'PIL'`（已實測）。
- 佔位圖只供剪輯預覽，不得用於發布。

## 8. 版權與 AI 揭露

- **受保護原作不用截圖**：漫畫格、動畫截圖、影集畫面一律不用。`source=screenshot` 預設禁止；若評論確有必要，須主控裁定，記入 sources.csv，並通過 CP-3。
- **公版圖像**（如古畫、公版插圖）：`source=stock`，`source_ref` 填出處與「公版」，主控確認枚舉用法。
- **AI 逼真圖像**（`photoreal=yes`）：發布時 YouTube Studio「AI use」勾 Yes；B 站創作者聲明勾選；說明欄寫明「本片圖像為 AI 生成，旁白為合成語音」。寫實描繪真實人物或真實事件，一律視為逼真。
- 歷史人物若史料無可考之肖像，不得生成「逼真肖像」並暗示為真實長相，改用構圖遠景、背影或器物特寫。
- `sources.csv` 必填：每張圖一列，無列者不得發布（對應 CP-3、CP-4）。

## 9. 數值規範

| 項目 | 數值 | 性質 |
|---|---|---|
| 圖幅 | 1920×1080，16:9 | 契約 |
| 換圖間隔 | 4–20 秒，依片型（見步驟 2） | 設計值 |
| 縮放幅度 | ≤ 1.15 | 02 §2.1 推論 |
| 單批張數 | ≤ 12 | 設計值 |
| 單張重試 | ≤ 3 次（含首次） | 設計值 |
| 段長估算 | 字數 ÷ 270 × 60 秒 | 與 script_to_shots 一致 |

## 10. 常見錯誤

- 合併後忘記把組內其餘段的 `image` 改為組第一段之路徑，導致同一圖被重複生成。
- 只在組首段寫 `image_prompt`，卻在後續段另寫不同提示詞。
- 角色外觀未取自 outline，同一人物在不同組長相不同。
- 直接沿用工具預設檔名、未改名，或未驗尺寸即進入渲染。
- 網頁逾時後自動重送，造成重複扣額度與多張不一致的圖。
- 以 `-I` 執行 make_placeholders.py。
- 佔位圖未替換即發布。
- 重跑 script_to_shots 後未檢查組與提示詞是否遺失。

## 11. 與其他 skill 銜接

- 上游：`recap-script-writer`（提供 script.md）、`recap-source-digest`（提供 outline.md 之人物表與風格聖經）。
- 圖像工具細節：`chatgpt-image-gen`、`browser-image-gen`、`stable-diffusion-cpp`、`grok-imagine-video`，本 skill 只定路由與規範，不抄其操作步驟。
- 角色卡與三視圖：`novel-characters` 可作為人物表來源。
- 下游：`recap-voice-subs`（manifest 之 duration 供步驟 2 使用）、`recap-render-publish`（讀取 shots.json 與 sources.csv，做 CP-3、CP-4 檢查）。

## 完成閘門

- [ ] `shots.json` 已由 `script_to_shots.py` 產生，欄位符合 CONTRACT（id、text、image、image_prompt、motion、source、source_ref）
- [ ] 共用場景已合併；組內每段 `image` 路徑一致；組首段檔名規則正確
- [ ] 換圖間隔落在片型區間內，單組不超過 20 秒，未跨章
- [ ] 每組有 image_prompt，含全片風格前綴、角色固定外觀（取自 outline）、負面提示
- [ ] 相鄰段 motion 不同；pan 方向不重複；縮放 ≤ 1.15
- [ ] `04_assets/images/` 每組一張 PNG，尺寸 1920×1080，已驗收（可開、非空白、無水印字）
- [ ] 無 `status=placeholder` 殘留，或已標明不得發布
- [ ] `image_gen_log.csv` 與實際檔案一致
- [ ] `sources.csv` 表頭依 CONTRACT，每張圖一列，`notes` 已填 `photoreal`
- [ ] 無 screenshot 來源；如有，已經主控裁定並記錄
- [ ] 寫實人物或事件之圖已標記 AI 揭露需求
- [ ] shots.json 之 source、source_ref 與 sources.csv 一致
