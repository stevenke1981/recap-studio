# Skill 撰寫共同規範（各 skill agent 必讀）

## 依據
- 研究：`<repo>\research\01-yedeng-analysis.md`（夜燈說書形式）、`02-genre-craft.md`（技法、數值、政策、檢查清單）、`03-toolchain.md`（本機工具）。
- 契約：`<repo>\templates\CONTRACT.md`（目錄、script.md、shots.json、manifest 格式）——skill 內容不得與之矛盾。
- 腳本：`<repo>\scripts\*.py`（先 `python <script> -h` 查實際參數，勿憑空寫參數）。

## 系列定位
「Recap Studio」skill 套組：以夜燈說書之做法（AI 原創寫實靜態圖＋AI 旁白＋章節化＋分層資產＋說明欄揭露模板）為骨幹，擴展至「一口氣看完」長片（30–180 分鐘）。不剪原作畫面、不用原聲。

| skill | 職責 |
|---|---|
| recap-video-studio | 總控：階段、閘門、目錄、調度其他 skill |
| recap-source-digest | 原作消化：分層摘要、story bible、人物表 |
| recap-script-writer | 口播稿：結構、hook、節奏、評論比重、字數預算 |
| recap-storyboard-art | 分鏡與配圖：shots.json、圖像提示詞、角色一致性、生圖路由、素材來源紀錄 |
| recap-voice-subs | 配音與字幕：TTS、發音詞典、對時、SRT |
| recap-render-publish | 合成與發布：渲染、BGM、響度、章節、標題縮圖說明欄、QA、合規 |

## 格式
- 檔案：`<repo>\skills\<name>\SKILL.md`，必要時加 `references/*.md`（長表格、模板放這裡）。SKILL.md ≤ 300 行。
- frontmatter：
  ```
  ---
  name: <name>
  description: <一段中文；寫明做什麼＋何時觸發（列觸發語：一口氣看完、解說影片、說書、recap…）；第三人稱>
  ---
  ```
- 正文：用途 → 輸入／輸出（路徑依契約）→ 步驟（可執行指令，路徑用 `<repo>\scripts\...`）→ 數值規範 → 檢查清單（完成閘門）→ 常見錯誤 → 與其他 skill 之銜接。
- 引用既有 skill 只寫名稱（如 `chatgpt-image-gen`、`novel-characters`、`omnivoice`），說明何時改用之；不抄其內容。
- 數值須來自研究報告；研究標「推論／設計值」者，skill 中寫「預設值，可依頻道數據調整」。
- 繁體中文；簡潔、命令式；不寫廢話。
- 只動自己的 skill 資料夾。不得 git 操作。

## 回報
產出檔案清單、各節摘要（5 條內）、與契約／腳本不一致之處（若有）。
