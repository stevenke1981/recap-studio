---
name: recap-render-publish
description: 將 recap 專案的分鏡、配音與字幕合成為長篇「一口氣看完」解說影片，並產出 YouTube 發布包（章節時間軸、標題、縮圖、說明欄）與上傳前合規閘門。涵蓋佔位圖、逐章與整片預覽、BGM 取得與 ducking、響度 -14 LUFS／TP -1 dBTP、qa_check。觸發語：渲染、render、預覽、合成影片、BGM、配樂、響度、LUFS、章節、chapters、縮圖、說明欄、標題、發布、上傳前檢查、AI 揭露、一口氣看完、解說影片、recap。本 skill 只產出檔案，不自動上傳；上傳屬公開發布，須主人明確同意。
---

> `<repo>` 指本 repo（recap-studio）之 clone 路徑，例如 `D:\recap-studio`。

# recap-render-publish

## 用途
將 `projects/<slug>/` 之分鏡、配音、字幕合成為 `07_render/final.mp4`，並於 `08_publish/` 備妥章節、標題、縮圖與說明欄。QA 全數 PASS 後交主人審閱。

## 輸入與輸出（依 `templates/CONTRACT.md`）

| 方向 | 路徑 | 說明 |
|---|---|---|
| 輸入 | `project.json` | 解析度、fps、`bgm`、`bgm_volume_db`、`loudness_lufs` |
| 輸入 | `03_storyboard/shots.json` | 章與段、圖片路徑、運鏡 |
| 輸入 | `04_assets/images/`、`04_assets/bgm/` | 圖與 BGM |
| 輸入 | `05_audio/manifest.json` + `*.mp3` | 須為 text_hash 最新 |
| 輸入 | `06_subs/full.srt` | 由 `build_subs.py` 產生，UTF-8 |
| 輸入 | `00_source/sources.csv` | 非 ai 素材與 BGM 來源紀錄 |
| 中間 | `07_render/chapters/chNN.mp4` | 章中間檔，**音軌為 ALAC，不得上傳** |
| 中間 | `07_render/preview/`、`07_render/preview.mp4` | 預覽（`--preview`） |
| 交付 | `07_render/final.mp4` | 整片，AAC 192k |
| 發布 | `08_publish/chapters.txt` | YouTube 章節 |
| 發布 | `08_publish/description.md` | 說明欄；**標題候選寫於其首節**（契約未定獨立標題檔，不新增） |
| 發布 | `08_publish/thumbnail.png` | 1280×720 |
| 發布 | `08_publish/qa_report.md` | `qa_check.py` 產出 |

## 前置條件
- `05_audio/manifest.json` 齊全（`tts_batch.py`），`06_subs/full.srt` 已由 `build_subs.py` 產生。
- `ffmpeg`、`ffprobe` 在 PATH；Pillow 已安裝；字幕字型 `Microsoft JhengHei`（微軟正黑體）可用。
- 下列指令假設 `P=<repo>\projects\<slug>`，腳本為 `<repo>\scripts\*.py`。

## 步驟

1. **佔位圖（可選，供預覽）**
   `python <repo>\scripts\make_placeholders.py %P%`
   只補缺圖，不覆寫真圖；`--force` 僅重生佔位圖。

2. **渲染前檢查**
   `python <repo>\scripts\qa_check.py %P% --pre-render`
   檢查圖片、manifest 與 text_hash、SRT、sources.csv。跳過 final.mp4 相關檢查。

3. **第一章定調（逐章預覽）**
   `python <repo>\scripts\render.py %P% --preview --chapter ch01`
   輸出 `07_render/preview/ch01.mp4`（720p、10 fps、ultrafast）。**不含 BGM 與字幕**（二者僅於整片組裝時加入）。檢查節奏（每段約 4–8 秒換圖）、運鏡、章節卡、留白與圖風一致性。定調後再改稿或圖，避免浪費整片渲染。

4. **整片預覽（BGM 與字幕試聽）**
   `python <repo>\scripts\render.py %P% --preview`
   輸出 `07_render/preview.mp4`，含 ducking 與字幕。預覽模式為單趟 loudnorm，**響度數字不作依據**。

5. **完整渲染**
   `python <repo>\scripts\render.py %P%`
   輸出 `07_render/final.mp4`（libx264 medium crf 20；兩趟 loudnorm）。

6. **章節時間軸**
   `python <repo>\scripts\make_chapters.py %P% [--min-seconds 10]`
   輸出 `08_publish/chapters.txt`。章名取自 shots.json；首行強制 `0:00`；短於門檻之章併入前章並警告；少於 3 章警告。

7. **QA 閘門**
   `python <repo>\scripts\qa_check.py %P%`
   輸出 `08_publish/qa_report.md`；exit 1 表 FAIL，須修至 PASS。

8. **發布包與合規** — 依 `references/publish-templates.md` 製作標題、縮圖、說明欄；依下節逐項勾選。

## 快取與重跑規則（render.py）
- 章快取：`07_render/chapters/chNN.hash`。指紋含渲染設定（尺寸、fps、preview、nvenc、fit）、章名、各項幀數與取樣數、運鏡，以及圖與音檔之 mtime 與大小。
- 改圖、改音、改 fps／nvenc／fit：該章重渲。改字幕、BGM、`bgm_volume_db`、響度：章快取不變，僅重跑整片組裝（final 無快取，每次完整組裝）。
- `--force`：忽略章快取，全部重渲。
- `--chapter` 使用與正式相同之快取路徑，故可先逐章渲染，最後整片組裝直接沿用。
- preview 與正式輸出目錄分開，互不污染。

## 長片建議
- **按章渲染**：逐章執行 `--chapter chNN`，失敗只重做該章；全部章完成後執行不帶 `--chapter` 之完整渲染，組裝 final.mp4。
- **`--jobs`**：預設 `min(4, CPU 核心數)`，為一章內片段並行編碼之數。加大前觀察 CPU 與記憶體，最佳值**未實測**。
- **`--nvenc`**：需 ffmpeg 含 `h264_nvenc`（腳本會檢查）。**本機 RTX 3060 Ti 未經實測**，畫質與速度皆未驗證；切換會使章快取失效。未驗證前預設不用，正式交付以 libx264 為準。
- **時間估計**：研究實測本機單張 5 秒 Ken Burns 約 1.2–1.4 秒（2× 預放大），故約 1,000 張圖約 20–25 分鐘（不含整片組裝與字幕燒錄之重新編碼，後者未實測）。
- **磁碟空間（推論，依 31 秒煙霧測試樣本換算，首章實測後校正）**：
  - 章中間檔約 0.4–0.7 GB／小時
  - final.mp4 約 0.3 GB／小時；preview.mp4（720p）約 0.35 GB／小時
  - 暫存：每章處理時產生 PCM wav，約 0.69 GB／小時，章完成即刪；最長 20 分鐘之章約需額外 230 MB
  - 建議預留：120 分鐘約 5 GB，180 分鐘約 8 GB 以上（不含圖與素材）

## BGM
**取得**（每首皆記入 `00_source/sources.csv`，`type=bgm`）
- 自製：`suno-song-creator` 生成。`source=ai`；`license` 欄記生成平台與方案之商用條款，並核實帳號方案可否商用。
- 免版權庫：YouTube Audio Library 或明確授權來源。`source=stock`；記 `license_url`。
- 禁止：原作 OP／ED、原作配樂、來源不明之音樂。Content ID 可能於數秒內認定並阻擋營利（研究 02 §3.3）。
- qa_check 只強制非 ai 之「段落素材」列於 sources.csv；BGM 不屬段落，**仍須人工記錄**（CP-3）。

**設定**
- 放置：`04_assets/bgm/<name>.mp3`；`project.json` 設 `"bgm": "04_assets/bgm/<name>.mp3"`。
- `bgm_volume_db`（預設 -22）：**旁白存在時** BGM 的目標音量（dB）。無旁白處 BGM 另加 +4 dB（render.py `BGM_LIFT_DB`），旁白下再由 sidechaincompress 壓低。
- Ducking 參數（render.py 內，非專案設定）：threshold 0.02、ratio 6、attack 20 ms、release 500 ms。
- 研究推論起始值：BGM 基準比旁白低 18–22 dB；有人聲時再壓 8–12 dB。**ducking 聽感未經實測**，以 `--preview` 整片試聽校正：旁白模糊則降低 `bgm_volume_db`（如 -24）；畫面空洞則提高（如 -20）。
- BGM 以 `-stream_loop -1` 循環至片長。短曲循環接縫須自行試聽，必要時選更長之曲。

## 響度
- 目標：整片 integrated **-14 LUFS**，true peak **≤ -1 dBTP**。
- render.py 以兩趟 loudnorm 正規化，TP 上限設 -1.5（較 -1 保守）。qa_check 容許 ±1 LU（`--lufs-tolerance`），TP 高於 -1.0 則 WARN。
- 只在整片組裝時正規化；**不得對章中間檔另行 loudnorm**，以免段間或章間響度跳動。
- 以 qa_check（ebur128）之數字為準，不以耳朵判定。研究期間於 3 段測試（旁白＋合成 BGM）實測得 -14.1 LUFS、TP -1.0 dBFS，**僅為單一樣本，正式片須重測**。

## 合規閘門（上傳前逐項勾選）
- [ ] `qa_check.py` 結論 PASS（無 FAIL）；每條 WARN 皆已說明或清除。**佔位圖 WARN 不得留存。**
- [ ] CP-2 稿件：原創評論字數比 ≥ 30%（內部設計值，非官方門檻）；逐字引文 ≤ 2–3 句；每章至少一段觀點；無純複述章。
- [ ] CP-3 素材：`sources.csv` 涵蓋所有非 ai 素材與 BGM；無原作畫面、原聲、原配樂。
- [ ] CP-4 AI 揭露：圖像逼真且描繪真人或真實事件、或仿冒他人聲音 → YouTube Studio 上傳流程中「變造或合成內容」（研究所記為 "AI use"，介面名稱以實際畫面為準）選 **Yes**，說明欄寫明。**保守原則：凡使用逼真 AI 圖像一律勾 Yes。** 動畫或插畫風、字幕、製作輔助（腳本、縮圖）通常不需揭露；一般 TTS 旁白通常不需，但仿冒他人聲音須勾。
- [ ] 重複使用與量產風險自查（YouTube inauthentic／reused content）：本片有獨有觀點與實質改寫，非純敘事拼接、非只換圖的同一敘事；與前幾部之結構、圖風、句型、BGM 有可辨識差異（CP-5：每 5 支做一次）。
- [ ] 說明欄含改編說明、史料／來源、圖像署名與授權、AI 揭露。
- [ ] 受保護原作（小說、漫畫、動漫、影集）：CP-1 已確認原作授權狀態與風險等級；若仍受保護，採評論主導格式，不用原畫面與原聲。
- [ ] CP-6：發布後 7 日檢視版權聲明、留存與評論。
- 以上為流程檢查點，非法律意見；平台政策會變動，上架前重讀官方頁。

## 上傳（公開發布，須明確同意）
- 本 skill **不自動上傳**，不呼叫任何上傳、發布或 API 工具。
- 產出完成後，列出 `final.mp4`、`thumbnail.png`、`description.md` 路徑與 QA 結論，請主人決定：上傳與否、可見性（公開、不公開、排程），以及頻道。未獲明確同意前不得上傳。
- 上傳後依 CP-6 追蹤；若需修正，改片後以新檔案重新上傳，須再次取得同意。

## 常見錯誤
1. **字幕路徑**：`06_subs/full.srt` 缺失時，render 僅 WARN 並輸出無字幕之影片；qa_check 會 FAIL。手改 ffmpeg filter 時路徑須用正斜線，冒號需跳脫（腳本已處理）。SRT 必為 UTF-8。
2. **ALAC 中間檔**：`07_render/chapters/*.mp4` 音軌為 ALAC，僅供組裝。交付與上傳只用 `07_render/final.mp4`（AAC）。
3. **兩個 chapters.txt**：`07_render/chapters.txt` 是 ffmpeg concat 清單，每次組裝覆寫；YouTube 章節是 `08_publish/chapters.txt`。
4. **佔位圖未替換**：qa_check 僅 WARN（exit 0），須人工確認。替換時注意 `resolve_image` 之優先序：`shots.json` 之 `image` 欄優先，其次 `04_assets/images/<id>.<ext>`。若佔位圖仍在 `image` 欄所指路徑，真圖放在別處也不會生效；覆寫同一路徑或更新 `image` 欄。
5. **text_hash 過期**：改 text、`pronunciations`、`voice` 或 `tts_rate` 後未重跑配音，manifest 之 hash 不符，qa_check FAIL。render 本身**不檢查 hash**，會以舊音訊渲染，故渲染前必跑 `qa_check --pre-render`。修復：`python <repo>\scripts\tts_batch.py %P% --only chNN`（hash 相同者會跳過）。
6. **以為單章預覽含 BGM 與字幕**：`--chapter` 之輸出無 BGM 亦無字幕，不可用來判斷混音或字幕。
7. **以預覽判響度**：`--preview` 為單趟 loudnorm，數字不可作交付依據。
8. **章節格式**：make_chapters 逐行決定 `M:SS` 或 `H:MM:SS`，故長片跨過 1 小時時同一檔會混用格式。建議人工統一為 `H:MM:SS` 後再貼入說明欄（研究建議，未經 YouTube 規格驗證）。
9. **短章併入**：make_chapters 會併入短於 10 秒之章，併入後章名以前章為準，須確認章節仍合理。

## 與其他 skill 之銜接
- `recap-voice-subs`：提供 `05_audio/manifest.json`、`06_subs/full.srt`；文字或發音改動須回其重跑 `tts_batch.py`。
- `recap-storyboard-art`：提供 `shots.json`、圖片與佔位圖；圖源記於 sources.csv。
- `recap-script-writer`：CP-2 不通過時退回改寫。
- `recap-source-digest`：CP-1 原作授權狀態與風險等級。
- `recap-video-studio`：總控，於發布階段呼叫本 skill。
- 外部 skill：`suno-song-creator`（BGM）、`chatgpt-image-gen`（縮圖底圖）。

## 驗證
- 腳本回歸：於 `<repo>` 執行 `python -m unittest tests.test_render -v`。
- 本 skill 所列指令均以各腳本 `-h` 與原始碼核對；NVENC、ducking 聽感、BGM 循環接縫與長片實際耗時皆**未驗證**。
