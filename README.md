# Recap Studio — 「一口氣看完」長篇解說影片製作流程與 Claude Code Skills

以 YouTube 頻道「夜燈說書」之製作形式（AI 原創寫實靜態圖＋AI 旁白＋章節化＋音軌／字幕與畫面分層＋說明欄揭露）為骨幹，擴展為 30–180 分鐘「一口氣看完」型解說長片之可重複流程。內含 6 個 Claude Code skills 與一套 Python／ffmpeg 製作腳本。

> 原則：不剪原作畫面、不用原聲；以原創評論（預設 ≥30%）＋ AI 示意圖改寫敘事；每支片記錄素材來源並揭露 AI 使用。

## 流程

```
S0 立項 ─ S1 原作消化 ─ S2 口播稿 ─ S3a 分鏡 ─ S4 配音字幕 ─ S3b 配圖 ─ S5 合成 ─ S6 QA 與發布
         outline.md     script.md    shots.json   mp3 + srt    images      final.mp4  chapters / 說明欄
```
「先音後圖」：音軌與字幕時間軸為骨，畫面可隨時重製而不動音軌（夜燈說書〈偷桃〉重製版即此做法）。詳見 [docs/WORKFLOW.md](docs/WORKFLOW.md)。

## Skills

| skill | 職責 |
|---|---|
| [recap-video-studio](skills/recap-video-studio/SKILL.md) | 總控：階段、閘門、風險分級、預覽迴圈、斷點續作、多 agent 派工 |
| [recap-source-digest](skills/recap-source-digest/SKILL.md) | 原作消化：四層階層摘要、story bible、人物表、主支線取捨 |
| [recap-script-writer](skills/recap-script-writer/SKILL.md) | 口播稿：字數預算、冷開場、章尾鉤子、評論層、口播規範、`script_stats.py` 閘門 |
| [recap-storyboard-art](skills/recap-storyboard-art/SKILL.md) | 分鏡配圖：圖組、風格聖經、角色一致性、生圖路由、運鏡、素材紀錄 |
| [recap-voice-subs](skills/recap-voice-subs/SKILL.md) | 配音字幕：edge-tts 選聲語速、發音詞典、對時、SRT 規範、替代引擎 |
| [recap-render-publish](skills/recap-render-publish/SKILL.md) | 合成發布：Ken Burns 渲染、BGM ducking、-14 LUFS、章節、標題縮圖說明欄、合規 |

安裝至 Claude Code（使用者層級）：
```powershell
pwsh ./install-skills.ps1        # 複製 skills/recap-* 至 ~/.claude/skills/
```
skill 內 `<repo>` 指本 repo 之 clone 路徑。

## 腳本（`scripts/`）

| 腳本 | 作用 |
|---|---|
| `script_to_shots.py` | `02_script/script.md` → `03_storyboard/shots.json`（切段、圖組、運鏡） |
| `tts_batch.py` | 逐段 edge-tts 合成、發音替換、句級字幕時間、快取與重試 → `05_audio/` |
| `build_subs.py` | 依時間軸產 `06_subs/full.srt`（每行 ≤16 字、≤2 行） |
| `make_placeholders.py` | 缺圖時產佔位圖，先出整片草稿 |
| `render.py` | 章節卡＋Ken Burns＋旁白＋BGM ducking＋loudnorm＋燒字幕 → `07_render/final.mp4`；`--preview`、`--chapter`、章級快取 |
| `make_chapters.py` | YouTube 章節時間軸 `08_publish/chapters.txt` |
| `qa_check.py` | 缺圖、配音過期、時長一致、響度、素材來源檢查 → `qa_report.md` |

資料格式見 [templates/CONTRACT.md](templates/CONTRACT.md)。

### 快速開始
```powershell
$P = "projects/demo-huapi"
python scripts/script_to_shots.py $P
python scripts/tts_batch.py $P
python scripts/build_subs.py $P
python scripts/make_placeholders.py $P      # 尚未備圖時
python scripts/render.py $P --preview       # 低解析快速預覽
python scripts/render.py $P                 # 正式輸出
python scripts/make_chapters.py $P
python scripts/qa_check.py $P
```

## 範例
`projects/demo-huapi/`：公版《聊齋志異・畫皮》白話改寫加評論，約 5.5 分鐘；含 project.json、outline、script、shots、字幕、章節、說明欄、QA 報告。生成之音訊、圖片、影片不入 repo（`.gitignore`），可依上列指令重建。

## 需求
- Python 3.11+（開發環境 3.14）、ffmpeg（含 libass）
- `pip install edge-tts pillow`
- 選用：ChatGPT／Gemini 網頁生圖（需登入）、stable-diffusion.cpp、Suno（BGM）、omnivoice／qwen3-tts（本機 TTS）

測試：`python -m unittest discover -s tests -t .`

## 研究
- [research/01-yedeng-analysis.md](research/01-yedeng-analysis.md)：夜燈說書形式分析與「一口氣看完」對照頻道
- [research/02-genre-craft.md](research/02-genre-craft.md)：劇本、視覺、音訊技法、平台政策與合理使用
- [research/03-toolchain.md](research/03-toolchain.md)：本機工具鏈盤點

研究中標「推論／設計值」之數字（評論比重、換圖間隔、懸念間距等）未經頻道留存數據校準。法律部分為資訊整理，非法律意見。

## 授權
MIT
