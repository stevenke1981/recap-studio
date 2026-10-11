# 共用契約：專案目錄與資料格式

所有 skill 與 scripts 皆依此契約；改動須經主控。

## 專案目錄 `projects/<slug>/`
```
project.json            # 專案設定（見下）
00_source/              # 原作筆記、素材；sources.csv 記錄每項素材來源
01_outline/outline.md   # 分層摘要（全書→卷→章→場景）、人物表
02_script/script.md     # 口播稿（格式見下）
03_storyboard/shots.json
04_assets/images/       # 每 segment 一圖：<segment_id>.png|jpg
04_assets/bgm/          # BGM 檔
05_audio/<segment_id>.mp3 + 05_audio/manifest.json
06_subs/full.srt
07_render/chapters/<chapter_id>.mp4, 07_render/final.mp4
08_publish/chapters.txt, description.md, thumbnail.png, qa_report.md
```

## project.json
```json
{
  "slug": "demo",
  "title": "一口氣看完《XXX》",
  "aspect": "16:9",
  "width": 1920, "height": 1080, "fps": 30,
  "voice": "zh-TW-HsiaoChenNeural",
  "tts_engine": "edge-tts",
  "tts_rate": "+0%",
  "target_minutes": 60,
  "segment_max_chars": 60,
  "subtitle_max_chars_per_line": 16,
  "bgm": "04_assets/bgm/main.mp3",
  "bgm_volume_db": -22,
  "loudness_lufs": -14,
  "pronunciations": {"重慶": "崇慶"}
}
```
未給之欄位由腳本以上述值為預設（見 `scripts/recap_common.py` DEFAULTS）。另有可選欄位：
- `chapter_card_seconds`（2.5）、`segment_gap_seconds`（0.25）
- `image_fit`：`cover`（預設，裁切填滿）｜`contain`（加黑邊）

## 00_source/sources.csv
UTF-8 with header：`asset_id,type,source,url_or_ref,license,used_in,notes`
- `asset_id`：圖檔名或 segment id；`type`：image|text|audio|bgm|history；`source`：ai|screenshot|original|stock|book|web
- `used_in`：segment id（多個以 `;` 分隔）。qa_check 要求所有非 ai 圖片在此有紀錄。

## script.md 格式
```
# 片名（不念）

## 第一章 標題        <- 一個 chapter；標題作章節卡與 YouTube chapters
旁白段落……（空行分段；一段可多句）

<!-- image: 圖像提示詞（可選，套用至下一段） -->
<!-- note: 製作備註，不念 -->

## 第二章 標題
……
```
規則：`#` 行不念；`## ` 開新 chapter；HTML 註解不念；其餘文字皆為旁白。

## shots.json
```json
{
  "version": 1,
  "project": "demo",
  "chapters": [
    {
      "id": "ch01",
      "title": "第一章 標題",
      "segments": [
        {
          "id": "ch01_s001",
          "text": "旁白文字（TTS 原文，未套發音替換）",
          "image": "04_assets/images/ch01_s001.png",
          "image_prompt": "",
          "motion": "zoom_in",
          "source": "ai",
          "source_ref": ""
        }
      ]
    }
  ]
}
```
- `id`：`ch{NN}_s{NNN}`，全片唯一，NN/NNN 由 1 起零補位。
- `motion` ∈ `zoom_in | zoom_out | pan_left | pan_right | static`；未指定則依序輪替。
- `source` ∈ `ai | screenshot | original | stock`；`source_ref` 填 URL／原作頁碼／生成工具。
- 多段可共用同一 `image`（同一場景）。
- segment 切分：依句末標點（。！？；…）累積至 `segment_max_chars` 為止，不切斷句子；單句超長時按逗號切。

## 05_audio/manifest.json
```json
{
  "segments": {
    "ch01_s001": {"file": "05_audio/ch01_s001.mp3", "duration": 7.42, "text_hash": "sha1", "subs": [{"start":0.0,"end":1.9,"text":"……"}]}
  }
}
```
`subs` 為段內相對時間之字幕片段（來自 TTS 字邊界或句邊界均分）。`text_hash` 相同則跳過重生（快取）。

## 時間軸
- 章節開頭插 `chapter_card_seconds`（預設 2.5 s）章節卡（無旁白，BGM 持續）。
- segment 之間 `segment_gap_seconds`（預設 0.25 s）靜音。
- 全片時間軸＝依 chapters 順序串接（章節卡＋各 segment 音長＋gap）。chapters.txt 與 full.srt 皆由此推得，須一致。

## 00_source/image_gen_log.csv（生成紀錄，選用）
`prompt_id,image,tool,status,attempt,started_at,size,note`；`status` ∈ `ok|retry|failed|placeholder`。公版圖之 `source` 以 `stock` 表示並於 sources.csv `license` 註明公版。
