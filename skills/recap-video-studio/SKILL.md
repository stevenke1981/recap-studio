---
name: recap-video-studio
description: 「一口氣看完」長篇解說影片（30–180 分鐘小說／漫畫／動畫／影集／歷史 recap、夜燈說書式說書影片）之總控 skill：定階段 S0–S6、完成閘門、人工審核點、先音後圖順序、預覽迴圈、斷點續作、多 agent 派工，並依序調度 recap-source-digest、recap-script-writer、recap-storyboard-art、recap-voice-subs、recap-render-publish 與 scripts。觸發語：一口氣看完、解說影片、說書影片、recap、長片解說、小說解說、動漫解說、歷史解說、做一支 60 分鐘的解說、續作／接續某個 recap 專案、查某專案做到哪一階段。
---

> `<repo>` 指本 repo（recap-studio）之 clone 路徑，例如 `D:\recap-studio`。

# recap-video-studio（總控）

## 用途
把「原作 → 一支可上傳的長篇解說影片」拆成 7 個可重入階段，每階段有輸入／輸出檔、機器閘門、人工審核點。本 skill 只管**順序、閘門、派工、風險**；各階段細節交子 skill，不在此重寫。

骨幹做法（取自夜燈說書研究，見 `<repo>\research\01-yedeng-analysis.md`）：AI 原創寫實靜態圖 ＋ AI 旁白 ＋ 章節化 ＋ 音軌／字幕與畫面分層 ＋ 說明欄揭露模板。**不剪原作畫面、不用原聲。**

## 鐵則
1. **先音後圖**：音軌＋字幕時間軸是骨，畫面可重製（見下節）。
2. **評論先行**：旁白評論／分析字數 ≥ 30%（設計值，無官方比例），每章 ≥ 1 段觀點；受保護原作加嚴（見風險分級）。
3. **零原作影音**：原聲 0 秒；原畫面預設 0。
4. **素材有帳**：非 AI 素材必記 `00_source\sources.csv`；BGM 授權可查。
5. **快取可重入**：任何階段中斷皆可重跑，已完成部分自動跳過。
6. **人工閘門不可略**：標「人工」之審核點，agent 不得自行放行；上傳／公開發布須主人明言，本流程止於備妥檔案。

## 路徑與變數
```
S = <repo>\scripts
P = <repo>\projects\<slug>      # slug：小寫英數與連字號
```
下列指令中 `$S`、`$P` 代入上述路徑（每次 Bash 呼叫需重設，或直接寫全路徑）。目錄與檔案格式以 `<repo>\templates\CONTRACT.md` 為準，本 skill 不得與之矛盾。腳本參數取自 2026-10-12 之 `-h`；腳本改版時以 `python <script> -h` 為準。

## 階段總覽（執行序）
| 階段 | 名稱 | 調用 | 主要產出 | 人工審核 |
|---|---|---|---|---|
| S0 | 立項 | 本 skill | `project.json`、目錄、風險等級 | H1 題材與風險 |
| S1 | 原作消化 | recap-source-digest（小說加 `novel-characters`） | `01_outline\outline.md` | H2 大綱與主線取捨 |
| S2 | 口播稿 | recap-script-writer | `02_script\script.md` | **H3 全稿（最重要）** |
| S3a | 分鏡（不出圖） | recap-storyboard-art | `03_storyboard\shots.json`（含 image_prompt） | H4 風格樣張 |
| S4 | 配音字幕 | recap-voice-subs | `05_audio\*`、`06_subs\full.srt` | H5 試聽 |
| S3b | 配圖 | recap-storyboard-art（`chatgpt-image-gen`／`browser-image-gen`／`stable-diffusion-cpp`） | `04_assets\images\*` | H4 抽檢 |
| S5 | 合成 | recap-render-publish（BGM：`suno-song-creator`） | `07_render\final.mp4` | H6 預覽樣片 |
| S6 | QA 與發布備料 | recap-render-publish | `08_publish\*` | **H7 上架前** |

S3 在使用者階段表中為「分鏡配圖」，實作拆成 S3a／S3b，**S3b 排在 S4 之後**（理由見「先音後圖」）。閘門指令之長版與可貼式檢查見 `references\stage-gates.md`。

---

## S0 立項
**做什麼**
1. 與主人確認：題材（作品名、作者、類型）、目標片長、平台（YouTube／B 站）、語言（預設繁中）。
2. **版權風險分級**（詳見 `references\source-type-branches.md`）：
   - A 公版（作者歿後保護期已滿的古典文學、史書原文）：夜燈模式。
   - B 歷史（史料＋現代研究）：史料為主，須史料清單與爭議聲明。
   - C 受保護、已完結／舊作：高評論比重，評論 ≥ 40%（設計值）。
   - D 受保護、熱門／連載中／仍販售／權利方積極維權：預設**建議換題**；堅持則降級為「評論主導」（評論 ≥ 50%，劇情複述 ≤ 50%），並由主人明確裁決。
   公版判定需查證（現代譯本、注釋本、標點整理本可能另有著作權）；本流程非法律意見。
3. **片長 → 字數預算**：`總字元數 = target_minutes × 250`（edge-tts 實測 267 字元／分再留停頓餘裕）。
   | 片長 | 字元預算 | 建議章數 | 建議配圖數（`segment_max_chars` 30–60） |
   |---|---|---|---|
   | 30 分 | 7,500 | 6–10 | 130–250 |
   | 60 分 | 15,000 | 10–16 | 250–500 |
   | 90 分 | 22,500 | 15–24 | 380–750 |
   | 120 分 | 30,000 | 20–30 | 500–1,000 |
   首次 TTS 後以實測總長回寫 cpm（見 S4），再校稿量。
4. 建目錄與 `project.json`：
   ```bash
   S=/d/recap-studio/scripts; P=/d/recap-studio/projects/<slug>
   mkdir -p $P/{00_source,01_outline,02_script,03_storyboard,04_assets/images,04_assets/bgm,05_audio,06_subs,07_render,08_publish}
   printf 'asset_id,type,source,url_or_ref,license,used_in,notes\n' > $P/00_source/sources.csv
   ```
   `project.json` 依契約填 `slug,title,target_minutes`，其餘用預設（`recap_common.DEFAULTS`）。常改欄位：`voice`、`tts_rate`、`segment_max_chars`、`pronunciations`、`bgm`。
5. 風險等級與主人裁決寫入 `$P\00_source\review_log.md`（本 skill 約定之記錄檔，非契約檔；每次人工閘門追加一行：日期、閘門、結論、簽核人）。

**閘門**（機器）
```bash
python -c "import json,sys;c=json.load(open(sys.argv[1]+'/project.json',encoding='utf-8'));assert c['slug'] and c['title'] and c['target_minutes']>0;print('ok',c['slug'])" $P
ls -d $P/0*_* | wc -l      # 應為 9 個目錄（00_source…08_publish 含 04_assets）
```
**人工 H1**：主人確認題材、風險等級；D 級須有明確裁決（CP-1）。

## S1 原作消化
調用 `recap-source-digest`：分塊 → 場景卡 → 章摘要 → 弧摘要 → logline／大綱 → story bible（人物表、地點、時間線、因果帳本、伏筆）。小說可先用 `novel-characters` 出角色卡。
- 輸入：`00_source\` 原作文本或筆記。輸出：`01_outline\outline.md`。
- 場景需有主線分；各弧篇幅與主線分成正比（研究 §1.2，設計值）。
- 閘門：`test -s $P/01_outline/outline.md`；內容檢查（logline、人物表、各弧摘要、八類連貫性錯誤 QA）依 recap-source-digest 之清單。
- **人工 H2**：看 logline、轉折清單、刪留取捨；受保護原作須確認「摘要到足以討論、不足以代替閱讀」。

## S2 口播稿
調用 `recap-script-writer`：hook（前 45 秒，含懸念、不劇透結局）→ 設定與承諾 → 4–6 弧主體（弧內每 60–90 秒節奏變化、每 3–5 分鐘小懸念，皆設計值）→ 高潮結局 → 評價回扣。章名用具畫面感短句；章即 YouTube chapters。
- 輸出：`02_script\script.md`（格式依契約：`## ` 開章，`<!-- image: -->` 可選）。
- 閘門（機器）：
  ```bash
  python $S/script_to_shots.py $P        # 能解析、列出章數／段數／字元數
  python -c "import sys;sys.path.insert(0,r'<repo>\scripts');from recap_common import *;from pathlib import Path;p=Path(sys.argv[1]);c=load_project(p);s=load_shots(p);n=sum(len(g['text']) for h in s['chapters'] for g in h['segments']);t=c['target_minutes']*250;print(n,t,'OK' if abs(n-t)<=t*0.05 else 'OFF')" $P
  ```
  字元數須在預算 ±5%。注意 `script_to_shots` 顯示之「est. duration」用 270 字元／分，與規劃值 250 不同；**以 S4 實測為準**。
- 其餘閘門（交 reviewer agent＋人工）：評論字數比 ≥ 30%（依風險等級加嚴）、每章 ≥ 1 段觀點、逐字引文 ≤ 2–3 句、無純複述章、單句 ≤ 30 字、數字口語化（CP-2）。
- **人工 H3**：全稿通讀。**稿件於此凍結**——S3 以後改稿雖有快取，但會連帶重做圖與音。

## S3a 分鏡（先不出圖）
調用 `recap-storyboard-art`：`python $S/script_to_shots.py $P` 產 `shots.json`，補 `image_prompt`、`motion`、`source`；定**風格前綴**（單一寫實影視風，全片一致）與角色一致性手段。
- 閘門：每段 `image_prompt` 非空、`source` 合法；`python -c` 檢查見 `references\stage-gates.md`。
- 重跑 `script_to_shots` 會依「文字完全相同」合併保留既有 image／image_prompt／motion／source，只動改過的段（`--force` 才覆蓋）。
- **人工 H4a**：先出 3–5 張風格樣張（章 1 代表場景＋主角）定調，再放行批量。

## S4 配音字幕（音軌為骨）
調用 `recap-voice-subs`。預設 edge-tts；備援 `omnivoice`、`qwen3tts-skill`、`xai-tts`；抽檢回聽可用 `qwen3-asr`。
```bash
python $S/tts_batch.py $P --only ch01      # 先試一章（可逗號多章）
python $S/tts_batch.py $P                  # 全量；hash 相同者跳過；失敗退避重試，exit 1 並列失敗 id
python $S/build_subs.py $P                 # → 06_subs\full.srt
python $S/make_placeholders.py $P          # 缺圖補佔位（真圖不會被覆蓋），供預覽與 QA
python $S/qa_check.py $P --pre-render      # 圖／音／字幕／素材帳檢查
```
- 輸出：`05_audio\<id>.mp3`、`manifest.json`（含 `text_hash`、`subs`）、`06_subs\full.srt`。
- **回寫語速**：總長 = `manifest` 各段 duration 加 gap 加章節卡（見 `references\stage-gates.md` 時間軸指令）。實測 cpm = 總字元 ÷ 總分鐘；與預算差 > 5% 則回 S2 增刪稿。
- 閘門：`tts_batch` exit 0；`build_subs` exit 0；`qa_check --pre-render` 無 FAIL（佔位圖僅 WARN）；總長與 `target_minutes` 差 ≤ 5%。
- 多音字／發音：寫入 `project.json` 之 `pronunciations`，只影響 TTS、不影響字幕；改後重跑 `tts_batch`（hash 變即重生）。
- **人工 H5**：試聽 ch01 全章與一個高密度章（發音、語氣、停頓）。

## S3b 配圖（時間軸已定）
調用 `recap-storyboard-art`：依 shots.json 逐段出圖，存 `04_assets\images\<segment_id>.png|jpg`（多段可共用同圖）。路由：已登入 ChatGPT／Gemini → `chatgpt-image-gen`／`browser-image-gen`；全本機 → `stable-diffusion-cpp`（8 GB VRAM 勿與 TTS 同時載入）；動態片段選配 `grok-imagine-video`。
- 利用 S4 時長：單段 > 12 秒的圖加張或換運鏡（規範見「數值規範」）。
- 每張非 AI 來源即時寫入 `sources.csv`；AI 圖可不列（`source: ai`）。
- 閘門：`python $S/qa_check.py $P --pre-render` 無 FAIL，且報告不再有「仍為佔位圖」WARN；解析度 WARN 須處理或說明。
- **人工 H4b**：抽看 10% 圖（臉孔／手部／文字亂碼／與旁白相符／無原作畫面或商標）。

## S5 合成
調用 `recap-render-publish`（BGM 用 `suno-song-creator` 或授權曲庫，放 `04_assets\bgm\`，`project.json` 設 `bgm`）。
```bash
python $S/render.py $P --chapter ch01 --preview   # 單章 720p 草稿（不做全片組裝）
python $S/render.py $P --preview                  # 全片草稿 → 07_render\preview.mp4
python $S/render.py $P                            # 正式 → 07_render\chapters\*.mp4、final.mp4
# 可選：--nvenc（NVENC 加速）、--jobs N、--no-subs、--no-bgm、--force
```
- 章檔以輸入＋設定 hash 快取；改一章只重渲該章。全片尾端兩段式 loudnorm 並燒字幕。
- 閘門：`final.mp4` 存在；`qa_check`（不加 `--pre-render`）無 FAIL（時長差 < 0.5 s、響度目標 ±1 LU）。
- **人工 H6**：看全片草稿的章界、字幕位置、BGM 壓人聲否、響度。

## S6 QA 與發布備料
```bash
python $S/make_chapters.py $P     # → 08_publish\chapters.txt（首行 0:00、≥3 章、每章 ≥10 s，過短自動併章並警告）
python $S/qa_check.py $P          # → 08_publish\qa_report.md；exit 1 即有 FAIL
```
`recap-render-publish` 產標題／縮圖／`description.md`（簡介、章節、原作與改編說明、AI 揭露、字幕說明、史料清單、圖像署名、留言問題）。
- 閘門：qa_report 無 FAIL；`description.md` 含 AI 揭露與作品／作者／導流正版；CP-3、CP-4 已記錄。
- **人工 H7**：決定 YouTube「AI use」與 B 站創作者聲明（保守：逼真 AI 圖一律勾 Yes）；主人自行上傳。上傳後 7 日回看版權聲明與留存曲線（CP-6）。

---

## 先音後圖：順序與理由
執行序：**S3a 分鏡 → S4 配音字幕 → S3b 配圖 → S5 合成**。
理由：
1. **音軌＋字幕時間軸是骨，畫面可重製。** 夜燈〈偷桃〉Flow 重製版說明欄明寫「沿用原有配音、配樂及字幕時間軸」只重製畫面（事實，https://www.youtube.com/watch?v=Fqvpr7FYAa8；由此推論畫面層可換而音軌不動）。
2. TTS 快而便宜（實測約 18× 即時，60 分約 3–5 分鐘；推論自 690 字 8 秒），生圖慢而不穩（需瀏覽器登入、可能被拒）。便宜且確定的先做，貴且不穩的後做。
3. 時長定了才知每圖停留幾秒、哪裡需加圖，並讓全片 `build_timeline` 完整（render／字幕／章節皆需每段都有音檔，缺一即 KeyError）。
4. 圖不合意只需重生該段圖；若先圖後音，改稿或換聲會牽動全部配圖節奏。
5. 缺圖時 `make_placeholders` 先頂位，即可在真圖到齊前出整片草稿驗證節奏與字幕。

## 預覽迴圈：先一章定調，再批量
1. S3a 風格樣張過 H4a。
2. `tts_batch --only ch01` → 試聽 → 調 `voice`／`tts_rate`／`pronunciations` 直到定案（改參數 hash 即變，重生很便宜）。
3. 全量 `tts_batch`（TTS 便宜；render 需全片音檔才能算時間軸）→ `build_subs` → `make_placeholders`。
4. **只替 ch01 出真圖**，`render.py $P --chapter ch01 --preview` → H6 風格決定。ch01 宜為含 hook＋設定的 2–3 分鐘章，才有代表性（設計值）。
5. 調整項：圖風前綴、運鏡、字幕長度（`subtitle_max_chars_per_line`）、BGM 音量、章節卡秒數。滿意後寫入 `review_log.md`「風格鎖」。
6. 批量放行：其餘章出圖 → 全片 preview → 正式 render。風格鎖後不再改風格前綴，否則全片不一致。

## 斷點續作
所有階段以「檔案存在＋hash」判斷是否重做，**中斷後從頭再跑同一指令即可**：
| 中斷點 | 續作做法 | 快取機制 |
|---|---|---|
| 改稿後 | `script_to_shots.py` 重跑 | 文字相同段保留 image／motion 等 |
| TTS 中途失敗 | 重跑 `tts_batch.py $P` | `text_hash`＝sha1(voice+rate+發音替換後文字)，相同且檔在即跳過 |
| 生圖到一半 | 已存在之 `<segment_id>` 圖保留；`qa_check` 列缺圖 | 檔案存在；`make_placeholders` 不覆蓋真圖 |
| 渲染中斷 | 重跑 `render.py $P` | 章檔 `.hash`＝輸入＋設定；未變即跳過；`--force` 強制 |
| 不知進度 | 跑 `references\stage-gates.md` 之「階段探針」 | 以產出檔判定 |
換聲／換語速／改發音後：`tts_batch` 自動重生受影響段，**隨後必須重跑 `build_subs`**，並重渲受影響章。接續前先讀 `review_log.md` 看哪些人工閘門已過。

## 多 agent 派工（大片預設）
小改動、單檔修正自己做；30 分鐘以上或章數 ≥ 8 時依下表分工（詳見 `references\multi-agent-dispatch.md`，含 brief 模板）。
| 階段 | 可並行單位 | 建議模型 |
|---|---|---|
| S1 | 分章／分卷場景卡 | Haiku 5.5 做場景卡；Sonnet 5.5 合併弧摘要與 story bible |
| S2 | 分弧撰稿（共用 story bible＋風格鎖） | Sonnet 5.5 寫；另一 Sonnet 5.5 審稿（評論比、連貫、TTS 友善） |
| S3a | 分章寫 image_prompt | Haiku 5.5（前綴與角色描述由主控定） |
| S4 | 分章 TTS | 腳本即可（`--only chNN`，勿多進程寫同一 manifest）；主控跑一次全量 |
| S3b | 分章生圖 | **瀏覽器登入限單一 Chrome，勿多 agent 同時操作同一帳號**；可並行者為本機 SD 與提示詞準備 |
| S5 | 腳本 `--jobs` | 主控 |
| S6 | QA 初審、說明欄初稿 | Haiku 5.5；風險與揭露終審 Sonnet 5.5＋人工 |
硬規則：各 agent 只動自己負責的檔案；共用檔（`project.json`、`manifest.json`、`shots.json` 整體、`sources.csv`、`review_log.md`）由主控整合；agent 不 git 操作。

## 原作類型分支（摘要）
- **公版古典（夜燈模式）**：改寫為白話，可較完整講述；仍須標原作／譯本出處、「白話改編非逐字朗讀」聲明；章名懸念化；圖用 AI 原創寫實圖，公版畫作整頁引用須記錄（`sources.csv`）。
- **受保護小說／漫畫／影視**：必走高評論比重（C ≥ 40%、D ≥ 50%）＋**原創 AI 示意圖**，不用原畫面、原聲、原配樂、原截圖；逐字引文 ≤ 2–3 句；結局以評價式呈現；片尾導流正版；主人須知悉風險（以摘要劇情為主之解說，在臺灣最難主張合理使用）。
- **歷史**：史料來源逐條列於說明欄；爭議處加「材料有歧見，本集不把 X 定成史實」類聲明；寫實 AI 人物像涉真實歷史人物，YouTube AI 揭露保守勾 Yes；公版畫像標年代與出處。
細節、檢查表、聲明範本見 `references\source-type-branches.md`。

## 數值規範（皆為預設值，可依頻道數據調整）
| 項目 | 值 | 性質 |
|---|---|---|
| 規劃語速 | 250 字元／分；edge-tts HsiaoChen +0% 實測 267 | 實測＋保守 |
| 圖片停留 | 4–8 秒為研究建議；夜燈實際 10–20 秒／圖；單段 > 12 秒加圖 | 推論／事實 |
| `segment_max_chars` | 30 ≈ 7 秒／段；60 ≈ 13 秒／段 | 算術 |
| 章節卡／段間靜音 | 2.5 s／0.25 s（契約預設） | 契約 |
| 章長 | 長片 3–6 分一章；夜燈短篇 1.5–2 分一章 | 設計值 |
| 響度 | -14 LUFS、真峰值 ≤ -1 dBTP；BGM 低旁白 18–22 dB，人聲段再壓 | 慣例 |
| 字幕 | 每行 ≤ 16–18 字、≤ 2 行；契約預設 18 | 契約／Netflix |
| YouTube 章節 | ≥ 3、首 0:00、每章 ≥ 10 s | 官方 |

## 完成閘門總清單
- [ ] H1 風險等級與題材已由主人確認，記入 `review_log.md`
- [ ] 稿量在預算 ±5%，實測總長與 `target_minutes` 差 ≤ 5%
- [ ] 評論比 ≥ 門檻、每章有觀點段、引文 ≤ 2–3 句（CP-2）
- [ ] `qa_check.py $P` 無 FAIL；無佔位圖
- [ ] `sources.csv` 涵蓋所有非 AI 素材；無原作畫面／原聲；BGM 授權可查（CP-3）
- [ ] AI 揭露已定（YT「AI use」、B 站聲明、說明欄文字）（CP-4）
- [ ] `chapters.txt` 與 `full.srt` 同源（皆由時間軸推得）
- [ ] 與前 4 支片的結構／圖風／句型／BGM 差異檢查（防 inauthentic，CP-5）

## 常見錯誤
- 先出一整批圖才發現要改稿或換聲 → 先音後圖，稿件凍結於 H3。
- 只對 ch01 跑 TTS 就 `render --chapter ch01` → 報「no audio for segment」；時間軸需全片音檔。
- 改了 `pronunciations`／`voice` 忘了重跑 `build_subs`，字幕與音軌漂移。
- `qa_check` 通過就上架：它不判斷評論比、AI 揭露、風格與內容正確，H3／H7 仍須人工。
- 所有影片同圖風同 BGM 同句型 → 頻道層級 inauthentic 風險；每支片須有獨有觀點與結構。
- 受保護熱門原作當 A 級處理；現代譯本當公版。
- 多 agent 同時寫 `manifest.json`／同時操作同一瀏覽器登入。
- 用 `--force` 當預設 → 失去快取，大片白耗時。

## 與其他 skill 銜接
recap-source-digest → recap-script-writer → recap-storyboard-art → recap-voice-subs → recap-render-publish；本 skill 在每個交接點驗閘門、寫 `review_log.md`、決定是否派工。腳本與契約有出入時，以契約為準並回報主控。
