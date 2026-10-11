# 03 本機工具鏈盤點（解說影片製作）

調查日期：2026-10-12
範圍：本機可用於「一口氣看完」長篇解說影片之工具鏈。
標示規則：【事實】為實測或讀檔所得；【推論】為依事實之判斷；【未驗證】為本次未實測者。

---

## 一、本機環境實測（只讀查詢，未安裝任何套件）

| 項目 | 結果 | 標示 |
|---|---|---|
| Python | `Python 3.14.7` | 事實 |
| ffmpeg | `ffmpeg version 8.1.1-full_build-www.gyan.dev`；configure 含 `--enable-libass`（可燒錄 ASS 字幕） | 事實 |
| ffmpeg loudnorm 濾鏡 | `ffmpeg -filters` 列出 `loudnorm  A->A  EBU R128 loudness normalization` | 事實（僅確認濾鏡存在；實際量測未執行） |
| ffprobe | `ffprobe version 8.1.1-full_build-www.gyan.dev` | 事實 |
| moviepy | **無法匯入**。於 `D:\recap-studio` 執行 `import moviepy` 報 `No module named 'moviepy'`；`pip show moviepy` 查無套件。於 `D:\moviepy` 執行則匯入本地原始碼 `D:\moviepy\moviepy\__init__.py`，但因缺 `proglog` 模組而失敗（`ModuleNotFoundError: No module named 'proglog'`）。 | 事實：目前 moviepy AE 分支不可直接使用，需補依賴或安裝 |
| edge_tts（Python 模組） | `import edge_tts` 成功 | 事實 |
| edge-tts CLI | 版本 `7.2.8` | 事實 |
| faster_whisper | 套件 `faster-whisper 1.2.1` 已安裝，但**匯入失敗**：`ModuleNotFoundError: No module named 'huggingface_hub'` | 事實：目前不可用，需修依賴（本次未安裝） |
| GPU | `NVIDIA GeForce RTX 3060 Ti`，8192 MiB，驅動 `595.97` | 事實 |

### edge-tts 中文聲音（`edge-tts --list-voices` 過濾 zh-TW／zh-CN，全部 11 個，未超過 20 筆）

| 語系 | 聲音 | 性別 | 風格標籤 |
|---|---|---|---|
| zh-TW | HsiaoChenNeural | Female | General；Friendly, Positive |
| zh-TW | HsiaoYuNeural | Female | General；Friendly, Positive |
| zh-TW | YunJheNeural | Male | General；Friendly, Positive |
| zh-CN | XiaoxiaoNeural | Female | News, Novel；Warm |
| zh-CN | XiaoyiNeural | Female | Cartoon, Novel；Lively |
| zh-CN | YunjianNeural | Male | Sports, Novel；Passion |
| zh-CN | YunxiNeural | Male | Novel；Lively, Sunshine |
| zh-CN | YunxiaNeural | Male | Cartoon, Novel；Cute |
| zh-CN | YunyangNeural | Male | News；Professional, Reliable |
| zh-CN | liaoning-XiaobeiNeural | Female | Dialect；Humorous |
| zh-CN | shaanxi-XiaoniNeural | Female | Dialect；Bright |

【事實】台灣口音可選：HsiaoChen、HsiaoYu（女）、YunJhe（男）。小說旁白若要男聲，zh-TW 僅 YunJhe 一位，zh-CN 男聲較多（Yunxi、Yunjian、Yunyang）。

---

## 二、edge-tts 實測（zh-TW-HsiaoChenNeural）

輸出位於 `D:\recap-studio\research\_probe\`。

### 樣本 A（短句，依任務指定文字）
- 文字：`這是一段測試旁白，用來估算語速。`（共 16 字含標點；漢字 14 個）
- 檔案：`probe_tw.mp3`、`probe_tw.vtt`
- 時長（ffprobe）：**4.08 秒**
- 字幕 VTT：單一 cue，`00:00:00,100 --> 00:00:04,075`，整句一條字幕（句級，無逐字時間）
- 換算：14 字 ÷ 4.08 秒 ≈ 206 字／分（短句含起始靜音與句尾停頓，偏低）

### 樣本 B（較長段落，128 字，漢字 116 個）
- 文字：一段約 128 字的小說式旁白（人工撰寫之測試文字，未使用任何原書內容）
- 檔案：`probe_long.mp3`、`probe_long.vtt`
- 時長（ffprobe）：**28.34 秒**
- 換算：116 字 ÷ 28.34 秒 ≈ **246 字／分**（漢字計）
- VTT：依標點切為多段 cue，末段 `00:00:19,675 --> 00:00:28,287`，即字幕切分為句級

### 結論（事實＋推論）
- 【事實】edge-tts 於本機可連線並成功產出 MP3 與 VTT，**網路正常，本次未失敗**；未使用任何 API key。
- 【事實】VTT 為句級時間戳，不是逐字時間。
- 【推論】以樣本 B 估算，`zh-TW-HsiaoChenNeural` 語速約 **240 字／分**（可接受區間 200–250 字／分，依文字標點密度而變）。
- 【推論】以此推估總字數：20 分鐘片長約 4,800–5,000 字；60 分鐘約 14,500 字；180 分鐘約 43,000–45,000 字（含停頓會更少；需留 5–10% 餘裕給 BGM 與段落間停頓）。
- 【未驗證】語速是否隨「情緒」或 `--rate` 參數變化，本次未測；`--rate` 未試。
- 【未驗證】long-form（>10 分鐘單次）是否有服務端限制，本次未測。

---

## 三、既有 skill 摘要（15 個，逐一讀取 `C:\Users\eda\.claude\skills\<name>\SKILL.md`）

欄位說明：「雲端／登入」欄：本機＝完全本地執行；雲端＝需網路服務；登入＝需帳號或瀏覽器已登入之 session。

### 3.1 配音類

| Skill | 用途 | 輸入 → 輸出 | 關鍵指令／用法 | 限制 | 雲端／登入 |
|---|---|---|---|---|---|
| **omnivoice** | 多語 zero-shot TTS；聲音克隆（3–10 秒參考音）、voice design、非語言符號（[laughter]）、中文拼音校正 | 文字＋參考音檔 → WAV（24 kHz） | Python API `ref_audio=...`；CLI `--ref_audio ... --output hello.wav`；批次 JSONL；Gradio demo | 模型約 2.45 GB；需 PyTorch（CUDA cu124 或 MPS）；RTF 宣稱 0.025 | 本機（首次需由 HuggingFace 下載模型）；Apache-2.0 |
| **qwen3tts-skill** | 阿里 Qwen3-TTS：CustomVoice（9 種內建音色＋自然語言指令）、VoiceDesign（文字描述造音色）、VoiceClone（3 秒參考音） | 文字 → WAV | `Qwen3TTSModel.from_pretrained(...)`；`generate_custom_voice / generate_voice_design / generate_voice_clone` | 1.7B 建議 VRAM ≥ 8 GB（本機 3060 Ti 8 GB 剛好、餘裕不足）；0.6B 建議 ≥ 4 GB；RAM ≥ 16 GB；建議 flash_attention_2 | 本機 |
| **xai-tts** | xAI TTS API（`POST https://api.x.ai/v1/tts`）或 console.x.ai 網頁 | 文字 → MP3／WAV | `curl`／Node／Python 範例；ffmpeg concat 分段後合併 | **需 `XAI_API_KEY`**；單次最多 15,000 字；429 為用量超限；支援 150+ 聲音、30+ 語言；ffmpeg `anullsrc` 做段落靜音 | **雲端**；API key 或網頁登入 |

### 3.2 語音辨識（轉寫／字幕時間）

| Skill | 用途 | 輸入 → 輸出 | 關鍵指令 | 限制 | 雲端／登入 |
|---|---|---|---|---|---|
| **qwen3-asr** | Qwen3-ASR-0.6B／1.7B 語音辨識；Qwen3-ForcedAligner-0.6B 強制對齊時間戳 | 音檔 → 文字（＋ token 級時間戳） | `pip install -U qwen-asr`；`Qwen3ASRModel.from_pretrained(...).transcribe(audio=...)`；`forced_aligner=` 開啟時間戳 | 52 語言、22 種中文方言；**ForcedAligner 單段上限 5 分鐘、僅 11 種語言**；不可用 `transformers.pipeline`；與 qwen-tts 之 transformers 版本警告可忽略 | 本機 |
| **cohere-transcribe** | Cohere Transcribe 2B（Conformer＋Transformer decoder），14 語言含中文 | 音檔 → 文字 | `AutoModelForSpeechSeq2Seq` ＋ `model.transcribe(processor=..., audio_files=..., language="zh")` | **不支援時間戳**（無字／句級）；transformers 需 `>=4.56,<5.3`，**5.0／5.1 不相容**；>35 秒自動切段 | 本機（首次由 HuggingFace 下載） |

### 3.3 畫面、影片、音樂生成（瀏覽器與雲端）

| Skill | 用途 | 輸入 → 輸出 | 關鍵指令／流程 | 限制 | 雲端／登入 |
|---|---|---|---|---|---|
| **chatgpt-image-gen** | 透過 chatgpt.com 網頁產生圖片並下載（非 API） | 提示詞 → PNG（ChatGPT 下載至 `~/Downloads`） | `agent-browser --cdp 9222` 連真實 Chrome；zh-TW UI 元素（新對話、傳送提示詞、儲存） | 依 skill 說明生成圖約 1024 px、需驗證實際檔案；輪詢超時不得自動重送；有拒絕回應需處理 | **雲端＋登入**（網頁 session） |
| **browser-image-gen** | ChatGPT 或 Gemini 網頁生圖之通用流程，強調驗證實際下載檔（尺寸、內容） | 同上 | 「先觀察、填入後回讀、送出、以下載檔驗收」 | 不得假設 4K 或去浮水印；需使用者既有登入 | **雲端＋登入** |
| **grok-imagine-video** | grok.com/imagine 生成 6s／10s 影片 | 提示詞（或參考圖）→ MP4 | `agent-browser --cdp 9222`；以 `aria-checked` 驗證 720p／10s 是否生效；以 `network requests --filter conversations/new` 驗證 HTTP 200 | **720p、10s 需登入**；2026-05-15 曾連續 500（後端中斷）；長寬比 16:9 等 | **雲端＋登入** |
| **ai-video-pipeline** | 組合層：ChatGPT 分鏡首幀 → Grok 片段（多參考圖）→ ffmpeg 抽末幀作連續性 → Suno BGM → ffmpeg 合成＋燒錄雙語 ASS 字幕＋`loudnorm`／sidechain 混 BGM，輸出 16:9 與 9:16 | 分段分鏡計畫 → 成片 | 專案結構 `prompts/ storyboard/ clips/ review_frames/ audio/ subtitles/ scripts/assemble_final.ps1`；ffmpeg 抽末幀 | 每段 Grok 需「全新頁面載入」；依賴上述瀏覽器 skill 與登入 | **雲端＋登入**（Grok、ChatGPT、Suno） |
| **suno-song-creator** | Suno 網站作曲並下載 MP3 | 歌詞＋風格標籤 → MP3 | `agent-browser --cdp 9222`；Download 為 **hover 子選單**（需 hover 再點 MP3 Audio）；產物於 `~/Downloads` | 建議 Pro 方案；歌詞標籤 `[Verse]／[Chorus]／[Instrumental]`；需登入 | **雲端＋登入** |
| **stable-diffusion-cpp** | leejet/stable-diffusion.cpp 本機推理（txt2img、img2img、ControlNet、LoRA、Flux、SDXL） | 提示詞 → PNG | 需自行 CMake 編譯（`-DSD_CUDA=ON`），二進位 `sd`／`sd-cli`；量化選擇表 | 需 CUDA Toolkit 與 ≥4 GB VRAM；Flux q4_k ≈ 6 GB、q3_k ≈ 5 GB、q2_k ≈ 4 GB；8 GB 卡可跑 SDXL 與量化 Flux；**本次未編譯** | **本機**（編譯需自備工具鏈） |
| **novel-characters** | 小說→角色設定集：分塊、角色掃描、角色卡、JSON／MD／離線 HTML；可選三視圖與真人身份固定圖 | 小說 txt → `<書名>-cast.json／.md`、`report.html` | `node "<SKILL_DIR>/scripts/novel-characters.mjs" chunk|merge ...`；Node.js 18+ | 無 npm 套件、無 API key；圖片步驟僅在圖像工具可用時執行；輸出保留逐字引文 | **本機**（文字流程）；圖像步驟依環境 |
| **moviepy-motion-designer** | 以 moviepy AE 分支（`import moviepy.ae as ae`）製作動畫成片：字幕動畫、片頭、Logo、轉場、粒子 | 一句需求 → MP4／GIF／16-bit master | 先草稿（`add_solid`）→ 關鍵幀檢查 → `write_videofile` 或 `ae.write_master`；`ae.motion.captions / title_card / beat_particles / transition` | `title_card` 與 `beat_particles` 需本機 Godot；中文需指定含中文字形之字型（缺字即報錯）；**目前本機 moviepy 缺 proglog，需先修依賴** | **本機** |

### 3.4 剪輯與桌面軟體

| Skill | 用途 | 輸入 → 輸出 | 關鍵指令／流程 | 限制 | 雲端／登入 |
|---|---|---|---|---|---|
| **video-editing** | 既有素材之剪輯工作流（ECC 來源）：Claude 規劃 → FFmpeg 切割 → Remotion → ElevenLabs／fal.ai → Descript／CapCut 精修 | 原始錄影 → 剪輯成片 | `ffmpeg -ss ... -to ... -c copy`；批次依 EDL 切段 | 重在「壓縮既有素材」而非從提示詞生成；Remotion、ElevenLabs、fal.ai、Descript 皆為外部服務（可選） | 部分**雲端**（ElevenLabs、fal.ai）；FFmpeg 部分**本機** |
| **jev-capcut** | 操作 CapCut **桌面版**（GPT 控制 Computer Use）：時間軸、靜圖秒數、平移縮放 keyframe、轉場、字幕、匯出 | 時間軸指令 → 匯出 MP4 | 先讀 `C:/Users/eda/Jev-ocu/skill/jev-desktop-context/SKILL.md`；每步截圖與 hash 驗證 | 僅限桌面版（非網頁、手機）；**不做 draft JSON 或 FFmpeg 偷渡**；剪映須標示為不同產品；Pro／登入提示不得自動接受 | **本機桌面＋CapCut 帳號**（依軟體而定） |

---

## 四、各製作階段建議工具鏈

標示：【本機】／【雲端】；【登入】表示需帳號或瀏覽器 session。

### 4.1 劇本（script）
- **首選**：Claude Code 本體撰寫，依 `novel-characters` 產出角色卡與故事摘要作為輸入。【本機】【無需額外登入】
- **備援**：無專用本機劇本 skill；可人工以分段大綱（`ai-video-pipeline` 的 storyboard 格式）手寫。
- 註：本機 skill 清單中另有 `wenyan-story-extender`、`article-writing` 等，**本次未逐一讀取，不納入本表**。

### 4.2 配音（TTS）
- **首選**：`edge-tts`（本機 CLI／Python 模組，已實測可用）。聲音：`zh-TW-HsiaoChenNeural`（女）、`zh-TW-YunJheNeural`（男）；語速約 240 字／分。【雲端：微軟 Edge 線上服務；無需 API key】【推論】
- **本機備援**：`omnivoice`（GPU、可聲音克隆、2.45 GB 模型）；`qwen3tts-skill` 之 CustomVoice 0.6B（8 GB VRAM 下較可行）。【本機】
- **雲端備援**：`xai-tts`（需 `XAI_API_KEY`，單次 15,000 字上限，分段後用 ffmpeg concat）。【雲端＋金鑰】

### 4.3 字幕（subtitles）
- **字幕文字來源**：劇本本身即為字幕文字，**不需 ASR**；若為既有音檔，才需轉寫。
- **時間軸**：
  - 首選：由 TTS 之 VTT（句級）或依段落時長推算。【本機】
  - 若需逐字對齊：`qwen3-asr` + `Qwen3-ForcedAligner-0.6B`（段長 ≤5 分鐘、限 11 種語言，中文可用）。【本機】
  - 備援：`faster-whisper`（已安裝，但目前**匯入失敗**，需先修 `huggingface_hub` 依賴，**本次未修**）。【本機】
  - `cohere-transcribe` **無時間戳**，不適合做字幕時間軸，僅適合純文字校對。
- **燒錄**：ffmpeg（已確認 `--enable-libass`），沿用 `ai-video-pipeline` 之 `.ass` 雙語字幕流程。【本機】

### 4.4 畫面（visuals）
- **首選（雲端）**：分鏡首幀用 `chatgpt-image-gen`（或 `browser-image-gen`）；動態片段用 `grok-imagine-video`。【雲端＋登入】
- **本機首選（靜態角色圖）**：`stable-diffusion-cpp`（需自行編譯 CUDA 版；SDXL 與量化 Flux 可於 8 GB 運行）。【本機】【未驗證】
- **本機替代（不生成實景）**：`moviepy-motion-designer` 製作圖卡、字幕動畫、Logo 揭示、轉場；適合「解說型」畫面（書封、人物卡、時間軸、地圖）。【本機；需修 moviepy 依賴】
- **片段連續性**：`ai-video-pipeline` 之末幀抽取（ffmpeg）。【本機】

### 4.5 BGM
- **首選**：`suno-song-creator`（網頁，器樂版需勾選 instrumental）。【雲端＋登入】
- **本機備援**：**本次盤點未發現本機 BGM 生成 skill**。可用 ffmpeg 或既有音檔混音（`ai-video-pipeline` 之 `sidechaincompress`＋`alimiter`）。【本機】
- **版權檢查點**：BGM 須記錄來源與授權（Suno 生成條款以官網為準，本次未查證）。

### 4.6 合成（assembly）
- **首選**：`ffmpeg`（concat、燒錄 ASS、`loudnorm` 響度、抽末幀、混 BGM）。`ai-video-pipeline/scripts/assemble_final.ps1` 為既有範本。【本機】
- **備援（動畫部分）**：moviepy AE 分支（需修依賴；`write_master` 可輸出 16-bit 無損）。【本機】
- **精修（桌面）**：`jev-capcut`（僅適合少量人工修剪，不宜作全自動主線）。【本機桌面＋帳號】

### 4.7 QA（品質檢查）
- **時長與格式**：`ffprobe`（format duration、stream codec、resolution、fps）。【本機，已可用】
- **響度**：`ffmpeg -af loudnorm=print_format=json`（I/O 量測）。濾鏡已存在，**量測尚未執行**。【本機】【未驗證】
- **字幕**：比對 ASS 時間軸與音訊時長；抽幀檢查燒錄字幕是否截斷。【本機】
- **音訊**：ffprobe 確認 BGM 與旁白流數；避免 BGM 蓋過旁白（sidechain）。
- **音畫同步**：以時間點抽幀比對（`ffmpeg -ss ... -frames:v 1`）。【本機】

---

## 五、主要風險與缺口

1. 【事實】**moviepy 不可直接匯入**（缺 `proglog`）；需由主控決定是否修依賴。本次未安裝。
2. 【事實】**faster-whisper 不可匯入**（缺 `huggingface_hub`）；影響備援轉寫路徑。
3. 【事實】**本機 BGM 生成 skill 缺口**；目前 BGM 只能走 Suno 雲端。
4. 【事實】Grok 720p／10s 需登入；2026-05-15 曾有後端 500 中斷。依賴網頁服務的製作流程，**可用性不受本機控制**。
5. 【事實】xai-tts 需 API key；edge-tts 不需金鑰但依賴線上服務。若網路中斷，配音主線即停擺。【推論】本機 TTS 唯一可離線之選項為 omnivoice 或 qwen3tts（需 GPU 與模型下載）。
6. 【推論】8 GB VRAM 同時載入 TTS 與影像生成模型可能不可行，應分階段執行。
7. 【未驗證】omnivoice、qwen3tts、qwen3-asr、cohere-transcribe、stable-diffusion-cpp **均未實際安裝或執行**；僅讀 SKILL.md。
8. 版權：本盤點不涉及任何原書內容；後續流程須依 BRIEF 補上合理使用比重、素材來源紀錄與 AI 內容揭露之檢查點。

---

## 六、來源

- 既有 skill 檔案（本機，唯讀）：
  - `C:\Users\eda\.claude\skills\ai-video-pipeline\SKILL.md`
  - `C:\Users\eda\.claude\skills\omnivoice\SKILL.md`
  - `C:\Users\eda\.claude\skills\qwen3tts-skill\SKILL.md`
  - `C:\Users\eda\.claude\skills\xai-tts\SKILL.md`
  - `C:\Users\eda\.claude\skills\moviepy-motion-designer\SKILL.md`
  - `C:\Users\eda\.claude\skills\video-editing\SKILL.md`
  - `C:\Users\eda\.claude\skills\qwen3-asr\SKILL.md`
  - `C:\Users\eda\.claude\skills\cohere-transcribe\SKILL.md`
  - `C:\Users\eda\.claude\skills\chatgpt-image-gen\SKILL.md`
  - `C:\Users\eda\.claude\skills\browser-image-gen\SKILL.md`
  - `C:\Users\eda\.claude\skills\grok-imagine-video\SKILL.md`
  - `C:\Users\eda\.claude\skills\suno-song-creator\SKILL.md`
  - `C:\Users\eda\.claude\skills\novel-characters\SKILL.md`
  - `C:\Users\eda\.claude\skills\stable-diffusion-cpp\SKILL.md`
  - `C:\Users\eda\.claude\skills\jev-capcut\SKILL.md`
- skill 內引用之外部來源（未另行連線查證）：
  - https://github.com/k2-fsa/OmniVoice ／ https://huggingface.co/k2-fsa/OmniVoice（omnivoice）
  - https://api.x.ai/v1/tts、https://console.x.ai（xai-tts）
  - https://github.com/leejet/stable-diffusion.cpp（stable-diffusion-cpp）
- 實測輸出：`D:\recap-studio\research\_probe\probe_tw.mp3`、`probe_tw.vtt`、`probe_long.mp3`、`probe_long.vtt`

## 七、未執行事項（誠實揭露）
- 未安裝任何套件（moviepy、faster-whisper 依賴皆未修）。
- 未執行 omnivoice、qwen3tts、qwen3-asr、cohere-transcribe、stable-diffusion-cpp、xai-tts、雲端網頁生成之任一項實測。
- 未執行 loudnorm 量測。
- 未查證 edge-tts 之服務條款與長時間使用限制。
