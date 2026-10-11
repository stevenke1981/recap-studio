# Recap Studio — 共用 Brief（各 agent 先讀）

## 目標
研究 YouTube 頻道「夜燈說書」之製作流程，制定一套可重複執行之「一口氣看完」長篇解說影片（小說／漫畫／動畫／影集／歷史 recap，片長 20–180 分鐘）製作流程，並落實為 Claude Code skills 與輔助腳本。

## 專案位置
- 根目錄：`D:\recap-studio`（git repo，agent 不得 git add/commit/stash/checkout）
- `research/`：研究報告（Markdown）
- `skills/<skill-name>/SKILL.md`：skill 本體（含 YAML frontmatter：name、description；description 須寫清觸發情境，中文為主）
- `scripts/`：Python 輔助腳本（Python 3.14，Windows；僅用 stdlib + 已裝套件：numpy、pillow、faster-whisper、edge-tts、moviepy（D:\moviepy 的 feat/ae-parity 分支）、ffmpeg CLI）
- `templates/`：腳本模板、分鏡 JSON schema 等
- `docs/`：流程總覽

## 本機環境
- Windows 10，RTX 3060 Ti 8GB，Python 3.14，ffmpeg 在 PATH
- 既有 skills 在 `C:\Users\eda\.claude\skills\`（唯讀參考）：ai-video-pipeline、omnivoice、qwen3tts-skill、xai-tts、moviepy-motion-designer、video-editing、qwen3-asr、cohere-transcribe、chatgpt-image-gen、browser-image-gen、grok-imagine-video、suno-song-creator、novel-characters、stable-diffusion-cpp、jev-capcut、skill-creator
- 新 skill 應「組合」既有 skill，不重寫其內容；引用時寫 skill 名稱。

## 硬規則
- 只動自己名下檔案（任務中指定之路徑）。
- 不新增必要依賴；需外部服務者（TTS 雲端、圖像網站）列為可選並給本機替代。
- 研究須附來源 URL；推論與事實分開標示（「事實」／「推論」）。查不到即寫查不到，不得杜撰頻道細節。
- 版權：流程須含合理使用／原創評論比重、素材來源紀錄、AI 內容揭露之檢查點。
- 繁體中文撰寫；程式碼、指令、檔名用英文。

## 回報格式（最後訊息）
1. 產出檔案清單（絕對路徑）
2. 重點結論 5–10 條
3. 未驗證／限制
