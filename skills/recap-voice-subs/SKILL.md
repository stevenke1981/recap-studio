---
name: recap-voice-subs
description: 負責「一口氣看完」長篇解說影片的配音與字幕：選定 zh-TW edge-tts 聲音與語速、以 tts_batch.py 逐段合成旁白並建 manifest.json、以 pronunciations 修正多音字與古文人名地名誤讀（只影響語音不影響字幕）、以 build_subs.py 產出 06_subs/full.srt，並含試聽第一章、快取重入、替代引擎（omnivoice、qwen3tts-skill、xai-tts）手工產 mp3 與 manifest、故障排除與完成閘門。當使用者提及配音、TTS、旁白語音、edge-tts、聲音選擇、語速、發音詞典、多音字、字幕、SRT、對時、manifest，或在 recap 專案流程中進入 05_audio／06_subs 階段時使用。
---

> `<repo>` 指本 repo（recap-studio）之 clone 路徑，例如 `D:\recap-studio`。

# recap-voice-subs

## 用途

把 `03_storyboard/shots.json` 之每段旁白合成為 `05_audio/<segment_id>.mp3`，並產出 `05_audio/manifest.json`（段長、字幕時間）與 `06_subs/full.srt`。配音與字幕由同一份 manifest 派生，確保與 `chapters.txt`、渲染時間軸一致。

上游：`recap-storyboard-art`（shots.json）。下游：`recap-render-publish`（讀 manifest 與 SRT）。
相關：`recap-script-writer`（口播稿）、`omnivoice`／`qwen3tts-skill`／`xai-tts`（替代引擎，見第 7 節）。

## 輸入與輸出（依 `templates/CONTRACT.md`）

| 方向 | 路徑 |
|---|---|
| 輸入 | `projects/<slug>/project.json`、`03_storyboard/shots.json` |
| 輸出 | `05_audio/<segment_id>.mp3`、`05_audio/manifest.json`、`06_subs/full.srt` |

`project.json` 與本 skill 相關欄位：`voice`、`tts_engine`（須為 `edge-tts` 才能用 `tts_batch.py`）、`tts_rate`、`subtitle_max_chars_per_line`、`pronunciations`。

## 1. 選聲

zh-TW 可選三聲（edge-tts，本機 CLI 列於研究 03 §一）：

| 聲音 | 性別 | 特色（官方標籤） | 建議題材（推論，需試聽） |
|---|---|---|---|
| `zh-TW-HsiaoChenNeural` | 女 | General；Friendly, Positive | 預設。一般敘事、現代題材、輕鬆解說 |
| `zh-TW-HsiaoYuNeural` | 女 | General；Friendly, Positive | 與 HsiaoChen 同屬女聲，研究未實測差異；適合作為備選或章節語氣變化之對照 |
| `zh-TW-YunJheNeural` | 男 | General；Friendly, Positive | 男性旁白、武俠／史詩／歷史題材（zh-TW 僅此一男聲） |

- 事實：三聲標籤相同，皆為 General；差異需由試聽判斷。
- 推論：長片（60 分以上）單一旁白易疲乏。可於 `project.json` 切換整片聲音；章內切換聲音目前 `tts_batch.py` 不支援（只讀 `project.json` 之單一 `voice`），需改稿或另案。
- 若需大陸口音男聲（如 zh-CN Yunxi、Yunjian、Yunyang），須主人裁決是否符合頻道風格；本流程以 zh-TW 為預設。

### 語速（實測，2026-10-12，本機 edge-tts 7.2.8）

樣本：194 漢字敘事段落，單次合成（研究 02 §1.4）。本次**未重測**。

| 聲音 | rate | 時長 | 漢字/分 | 字元/分（含標點） |
|---|---|---|---|---|
| HsiaoChen | -10% | 54.2 s | 215 | 240 |
| HsiaoChen | +0% | 48.8 s | 239 | 267 |
| HsiaoChen | +10% | 44.4 s | 262 | 294 |
| YunJhe | -10% | 48.9 s | 238 | 266 |
| YunJhe | +0% | 44.0 s | 265 | 296 |
| YunJhe | +10% | 40.0 s | 291 | 325 |

- 規劃用換算（推論，保守）：HsiaoChen +0% 取 **250 字元/分**；稿量＝片長（分）× 250。
  - 30 分約 7,500 字；60 分約 15,000 字；90 分約 22,500 字；120 分約 30,000 字（均為字元數，含標點）。
- 建議語速（推論）：解說敘事 -5% 至 +0%；高資訊密度段可 +5%，不超過 +10%。
- **第一次實合成後，須以實際總長回寫 cpm（字元/分）再校稿量**，不可硬套上表。
- 語速設定：`project.json` 之 `tts_rate`（字串，如 `"-5%"`、`"+0%"`）。`tts_batch.py` 無 `--rate` 參數。改 rate 會改變 `text_hash`，使全片句段重生。

### 試聽流程（先跑第一章）

1. 確認 `project.json`：`tts_engine: "edge-tts"`、`voice`、`tts_rate`、`pronunciations`。
2. 只合成第一章：

   ```
   python <repo>\scripts\tts_batch.py <repo>\projects\<slug> --only ch01
   ```

3. 試聽 `05_audio/ch01_s001.mp3`、中段一段、末段一段（至少 3 段）。
4. 比對 `manifest.json` 之 `duration`：`ch01` 總字元數 ÷ cpm × 60 應落於估計值 ±10% 內；偏差大表示語速或停頓設定需調整。
5. 聽感不合（過快、拖沓、誤讀）→ 調 `tts_rate` 或 `pronunciations`，`--only ch01` 重跑（僅變動句段重生，見第 3 節）。
6. 第一章定案後才跑全片。

注意：`build_subs.py` 要求**所有 shots 段皆有音檔**，只跑 `--only ch01` 時無法對第一章單獨建 SRT（見第 6 節）。試聽階段以 manifest 之 `subs` 內容檢查即可。

## 2. 指令

### 2.1 `tts_batch.py`（已以 `-h` 與原始碼確認）

```
python <repo>\scripts\tts_batch.py <project_dir> [--only ch01[,ch02]] [--concurrency N] [--force] [--boundary WordBoundary|SentenceBoundary]
```

| 參數 | 預設 | 說明 |
|---|---|---|
| `project_dir` | 必填 | 專案根目錄（含 `project.json`） |
| `--only` | 全部 | 章節 id，逗號分隔；未知 id 報錯（exit 2） |
| `--concurrency` | 4 | 同時合成段數；服務端限流時降為 1–2 |
| `--force` | 關 | 無視快取全部重生 |
| `--boundary` | `WordBoundary` | 字／句邊界事件來源，供字幕對時（見下） |

- 每段失敗會重試 3 次（退避 1、2、4 秒），仍失敗者列於 stderr（`FAILED <id>: ...`），結束碼 1；成功段仍寫入 manifest。
- 輸出訊息：`generated: N  skipped (cached): M  failed: K`。
- 需求：`ffprobe` 於 PATH（段長量測）。
- `--boundary`：WordBoundary 提供逐詞事件，字幕錨點較細；字幕錯位時可改 `SentenceBoundary` 並加 `--force`。注意 **boundary 不在 `text_hash` 內**，改 boundary 不會自動重生，必須 `--force`。

### 2.2 `build_subs.py`（已以 `-h` 與原始碼確認）

```
python <repo>\scripts\build_subs.py <project_dir>
```

- 讀 `shots.json`、`manifest.json`、`project.json`，時間軸由 `build_timeline`（章節卡 `chapter_card_seconds` ＋段音長 ＋ `segment_gap_seconds`）派生，與 chapters 一致。
- 每段 manifest `subs` 先經 `wrap_lines` 切為 `subtitle_max_chars_per_line` 字一行，每 cue 最多 2 行；超出則拆 cue，時間依字數比例分配。
- 行末去除 `，、。,.；;：:` 等（句號、逗號）；`！？` 保留。
- 輸出：`wrote <path>: N cues, last cue ends at H:MM:SS`。

### 2.3 快取與重入

- `text_hash = sha1(voice + tts_rate + 替換後文字)`。hash 相同且 mp3 存在 → 跳過。
- 改稿字 → hash 變 → 該段重生；改 `voice`／`tts_rate`／`pronunciations`（影響替換後文字者）→ 相關段重生。
- 改 `--boundary` 不會使快取失效，需 `--force`。
- 失敗段不寫入有效 entry，重跑即補做，成功段不重做。
- 中斷時會殘留 `*.mp3.part`，可安全刪除。
- manifest 會剔除 shots 中已不存在的段。
- 執行中斷也會寫入已完成段的 manifest（`finally` 區塊）。

## 3. 發音詞典（`project.json` → `pronunciations`）

- 格式：`{"原字詞": "替換寫法"}`，**只影響送入 edge-tts 的文字**；manifest `subs` 與 `full.srt` 仍顯示原文。
- 替換為子字串全域取代，長詞優先；單字鍵會誤傷所有出現處，應以完整詞為鍵。
- edge-tts 無法指定拼音，只能以字替換，替換字須同讀且語意不變（或經主人確認）。
- 詳細候選表（多音字、古文人名地名）、偵測流程（掃描→聽寫抽查→試聽→更新詞典→重生）見 `references/pronunciation.md`。

## 4. 字幕規範

- 每行 ≤ 16–18 字（契約預設 `subtitle_max_chars_per_line: 18`；Netflix 繁中規範為 16，建議長片採 16，寫入 `project.json` 後統一）。
- 每 cue ≤ 2 行。
- 全形標點；行末不加逗號、句號、頓號（`build_subs.py` 會自動去除）。問號、驚嘆號保留。
- 成人節目閱讀速度上限 9 字/秒（Netflix）；解說旁白實測約 4–5 字/秒，一般不會超速。
- 字幕文字取自 `shots.json` 之 `text`（原文），**不含替換後文字**。
- 單行字幕顯示不足 1.0 秒或超過 6 秒（推論）→ 檢查 cue。
- 雙語字幕（後續擴充，**目前未實作**）：主字幕為中文，英文以小字副行顯示（「夜燈模式」為主人指定之選項名稱，細節未定義）。需主控裁決：CONTRACT 新增 `subs_en` 欄位或另產一檔；ASS 樣式亦須決定。現行 `build_subs.py` 只輸出單語 SRT。

## 5. 替代引擎

### 5.1 現況

`tts_batch.py` **只支援 edge-tts**。`project.json` 之 `tts_engine` 非 `edge-tts` 時會報錯拒絕執行（`tts_engine '...' is not supported here`），以免混用引擎造成風格不一。

| 引擎 | 性質 | 特點 | 限制 |
|---|---|---|---|
| `edge-tts`（預設） | 雲端（微軟 Edge 線上服務），無需 API key | 本機已實測可用 | 依賴網路；單一 voice 無完整 SSML |
| `omnivoice` | 本機，GPU | 聲音克隆（3–10 秒參考音）、中文拼音校正、非語言符號 | 模型約 2.45 GB；需 PyTorch（CUDA 或 MPS） |
| `qwen3tts-skill` | 本機，GPU | CustomVoice 內建音色＋自然語言指令；VoiceDesign 以文字造音色；VoiceClone | 1.7B 建議 VRAM ≥ 8 GB（本機 3060 Ti 8 GB 餘裕不足）；0.6B 建議 ≥ 4 GB |
| `xai-tts` | 雲端，需 `XAI_API_KEY` | 150+ 聲音、30+ 語言；單次 ≤ 15,000 字 | 需金鑰（費用與金鑰管理須主人同意）；429 為用量超限 |

- 分角色演繹（如人物對白換聲）可由 omnivoice／qwen3tts-skill 完成；對白須標示，且**不得仿冒真人聲音**（研究 02 §3.1、§4.3）。
- 聲音克隆須有參考音之授權，使用前須主人確認。
- 任何新費用、金鑰、雲端帳號，須先請主人裁決。

### 5.2 自行產出 mp3 與 manifest

若改用他引擎，須自行產出並依 `templates/CONTRACT.md` 寫入 `manifest.json`：

1. 每段輸出 `05_audio/<segment_id>.mp3`（建議 48 kHz、同一聲道配置，便於後續混音）。
2. 段長量測（秒，小數 3 位）：

   ```
   ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "<repo>\projects\<slug>\05_audio\<segment_id>.mp3"
   ```

3. 字幕 `subs`（段內相對時間）：
   - 有引擎時間戳 → 直接使用，`text` 為原文（非替換後文字）。
   - 無時間戳 → 以 `tts_batch.py` 之 `even_subs` 依字數均分（與 edge-tts 無事件時之備援相同）：

     ```
     python -c "import sys; sys.path.insert(0,r'<repo>\scripts'); from tts_batch import even_subs; from script_to_shots import sentence_pieces; print(even_subs(sentence_pieces(TEXT, 36), DURATION))"
     ```

     （`TEXT`、`DURATION` 代入實值；`36` 為 `subtitle_max_chars_per_line × 2`。）
4. `text_hash`：依 `tts_batch` 定義 `sha1(voice + tts_rate + 替換後文字)` 計算，格式一致以便日後切回 edge-tts 時快取語意不混亂。
5. 寫入 manifest（保留既有 entries，只更新本次段）：

```json
{
  "segments": {
    "ch01_s001": {
      "file": "05_audio/ch01_s001.mp3",
      "duration": 7.42,
      "text_hash": "<sha1 hex>",
      "subs": [
        {"start": 0.0, "end": 1.9, "text": "第一句原文，"},
        {"start": 1.9, "end": 7.42, "text": "第二句原文。"}
      ]
    }
  }
}
```

- `subs.text` 為**原文**（非替換後），`build_subs.py` 依此產字幕。
- 注意：他引擎產出之段不可再交給 `tts_batch.py` 處理（會被拒絕）；`tts_engine` 欄位應保留為實際使用之引擎名，以標示來源（如 `"omnivoice"`），並於專案工作日誌記錄。
- 注意：研究 02 §5.3 建議時間軸以 PCM 取樣數累加而非 MP3 時長；本流程沿用契約之 ffprobe 段長，長片累積漂移尚未實測。

## 6. 故障排除

| 症狀 | 原因（推論／已知） | 處置 |
|---|---|---|
| `FAILED ...: RuntimeError: edge-tts returned no audio`、連線錯誤、timeout | edge-tts 網路不穩或服務端限流（錯誤名稱依實際輸出為準，未逐一列舉） | 先確認網路；`--concurrency 1` 重跑；已成功段會跳過，重跑即補做 |
| `AttributeError: module 'aiohttp' has no attribute 'ClientTimeout'` | 研究 02 §5.2 曾於本機偶發，原因未查明 | 直接重跑通常可恢復；持續發生則檢查 aiohttp 版本 |
| `ModuleNotFoundError: No module named 'edge_tts'` | 未安裝 | `python -m pip install --user edge-tts` |
| `pip show edge-tts` 顯示 `Version: None`（但 `import edge_tts` 成功） | 本機 dist-info 損壞（2026-10-12 盤點時觀察到） | `python -m pip install --user --ignore-installed edge-tts` |
| `ffprobe not found on PATH` | ffmpeg 未在 PATH | 確認 `ffprobe -version` |
| `unknown chapter(s) [...]` | `--only` 章節 id 錯誤 | 對照 shots.json 之 chapters.id |
| `tts_engine 'X' is not supported here` | `project.json` 非 `edge-tts` | 若用他引擎，見第 5 節；否則修正設定 |
| `KeyError: no audio for segment ...`（build_subs） | 尚有段未合成（例如只跑 `--only ch01`） | 先完成全片 `tts_batch`；試聽期間以 manifest 檢查 |
| 字幕與語音對不上（偏早／偏晚） | 字邊界事件與替換文字錯位，或 boundary 不適合 | 比對 manifest `subs` 首尾時間與音檔；改 `--boundary SentenceBoundary --force` 重試；仍不準時回報主控裁定（例如改為段內均分） |
| 某段字幕不見或只剩數字 | `subs` 為空或 `text` 全為標點 | 檢查 `shots.json` 該段 text；刪除 manifest 該段後重跑 |
| 聲音突然變了 | `voice` 或 `tts_rate` 改動 | 屬預期（hash 變）；若非預期，檢查 project.json 版本 |
| 改了 pronunciations 卻沒變 | 替換鍵與稿件字形不一致（如簡繁）或鍵過短被先匹配 | 核對鍵的字形與長度；`--only` 指向正確章 |
| Windows 主控台中文亂碼 | 終端機編碼 | 執行前 `PYTHONIOENCODING=utf-8` |

## 7. 與其他 skill 之銜接

- `recap-script-writer`：提供口播稿（字數與 cpm 估算依本 skill 第 1 節）。
- `recap-storyboard-art`：提供 shots.json 之 `text` 與 `id`；改 text 會使該段重生。
- `recap-render-publish`：讀取 `manifest.json`（段長）與 `full.srt`；章節時間與 SRT 由同一時間軸派生。
- `omnivoice`、`qwen3tts-skill`、`xai-tts`：替代引擎之安裝與用法以各 skill 為準；本 skill 只規定輸出格式（第 5 節）。

## 8. 完成閘門（全部通過才交下游）

- [ ] `project.json`：`tts_engine`、`voice`、`tts_rate`、`pronunciations` 已定案，並有記錄。
- [ ] `tts_batch.py` 全片執行，exit code 0，`failed: 0`。
- [ ] manifest 段數 ＝ shots.json 段數（以 id 比對，無缺漏、無多餘）。
- [ ] `05_audio/` 每段 mp3 皆存在，且 manifest `duration` > 0。
- [ ] `build_subs.py` 執行成功，`06_subs/full.srt` 存在，cue 數 > 0。
- [ ] SRT 抽查：每行 ≤ 設定字數、≤ 2 行、無行末逗號句號。
- [ ] 抽聽 3 段（首段、中段、末段）：語速、誤讀、停頓正常。
- [ ] 多音字掃描與聽寫抽查已做（`references/pronunciation.md` 第 4 節），結果已記錄。
- [ ] 最後一句之 SRT 結束時間 ≈ 全片時間軸總長（誤差 ≤ 0.1 s）。
- [ ] 若用他引擎：manifest 格式符合 CONTRACT；`text_hash` 與 `subs.text`（原文）已核對。

## 常見錯誤

- 以單字作為 pronunciations 的鍵，誤傷全稿。
- 改 `--boundary` 後未加 `--force`，以為已生效。
- 只跑 `--only` 即執行 build_subs。
- 字幕寫入替換後文字（應為原文）。
- 以 `pip show` 判斷套件是否可用，而非實際 import。
- 未試聽第一章即跑全片，浪費配額與時間。
