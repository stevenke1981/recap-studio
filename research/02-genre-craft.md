# 02 — 「一口氣看完」長篇解說影片：創作技法與平台規範研究

> 研究日期：2026-10-12。範圍：劇本、視覺、音訊、平台規範、長片工程。本檔不涉「夜燈說書」頻道細節（另有他人負責）。
> 標示約定：**【事實】**＝有來源可查；**【實測】**＝本機實跑得到之數據；**【推論】**＝作者依經驗／常理推出，無直接來源，須以頻道後台數據校準；**【查不到】**＝已搜尋而無可靠來源。
> 法律事項非法律意見；各平台政策會變，上架前須重讀官方頁。

---

## 0. 速覽：可直接寫入 skill 的數值表

| 項目 | 數值 | 性質 |
|---|---|---|
| 中文 TTS 語速（edge-tts zh-TW-HsiaoChenNeural, rate +0%） | 239 漢字/分、267 字元(含標點)/分 | 【實測】 |
| 同上 YunJheNeural +0% | 265 漢字/分、296 字元/分 | 【實測】 |
| rate -10% / +10%（HsiaoChen） | 215／262 漢字/分 | 【實測】 |
| 規劃用換算（保守，含停頓） | **250 字元/分**（Hsiao 預設）；規劃稿量＝片長分鐘 × 250 | 【推論】基於實測再留停頓餘裕 |
| 稿量對照 | 30 分≈7,500 字；60 分≈15,000；90 分≈22,500；120 分≈30,000 | 【推論】算術 |
| 響度 | 成片 **-14 LUFS 積分、真峰值 ≤ -1 dBTP** | 慣例；YouTube 無官方公布目標【事實】 |
| 字幕 | 每行 ≤ 16 字、≤ 2 行、成人 ≤ 9 字/秒、全形標點、句末不加句號 | Netflix 繁中規範【事實】 |
| YouTube 章節 | ≥ 3 個、首個 00:00、遞增、每章 ≥ 10 秒 | 官方【事實】 |
| 靜態圖停留 | 4–8 秒/張，隨句界切換；單句超過 8 秒則多圖或同圖換運鏡 | 【推論】（軟體預設 5 秒為【事實】） |
| 原創評論比例（內部門檻） | 旁白中「評論／分析／觀點」字數 ≥ 30%，且每章 ≥ 1 段 | 【推論】（無任何官方百分比） |
| 原作影音素材 | 原聲 0 秒；原畫面預設 0，必要時 ≤ 單張靜態且為評論所必要 | 【推論】風險控管 |

---

## 1. 劇本：從長篇原作壓縮為 30–120 分鐘口播稿

### 1.1 分層摘要法（hierarchical summarization）

**【事實】** OpenAI「Recursively Summarizing Books with Human Feedback」以遞迴任務分解處理整本書：先濃縮短段落，再反覆濃縮濃縮結果直到得出全書摘要。（<https://arxiv.org/abs/2109.10862>）

**【事實】** BooookScore（ICLR 2024）比較兩法：
- 階層合併（hierarchical merging）：連貫性較高，但細節較少。
- 增量更新（incremental updating）：細節較多，但連貫性較低；僅在超大上下文（Claude 2 於 88K 字元塊）時追平。
- 2K token 分塊下 BooookScore：Claude 2 階層 91.1／增量 78.6；GPT-4 89.1／82.5。更大分塊不改善階層合併。
- 歸納出 8 類連貫性錯誤：實體省略、事件省略、因果省略、不連貫、顯著性（塞入與主線無關的細節）、語言、前後矛盾、重複。
- 來源：<https://arxiv.org/html/2310.00785v4>

**推薦流程（【推論】，依上述研究設計）：**

| 層 | 單位 | 產出（結構化 JSON，非散文） | 建議長度 |
|---|---|---|---|
| L0 | 原文 chunk（章／場景，≤ 約 2–4K tokens；過長章按場景切） | — | — |
| L1 | 場景卡 scene card | who / where / goal / conflict / outcome / 情緒值 / 是否主線 / 金句候選 | 80–150 字 |
| L2 | 章摘要 | 事件鏈（因果句）、人物變化、伏筆 | 150–300 字 |
| L3 | 卷／篇章弧摘要 | 弧的起承轉合、主線進度、本弧最大轉折 | 300–600 字 |
| L4 | 全書 logline + 大綱 | 一句話主題、主角欲望／阻礙／代價、全書 5–9 個大轉折 | 500–1,000 字 |

- 同步維護 **故事聖經 story bible**（人物表、地點、時間線、因果帳本、已埋未收伏筆）。每個 L1→L2 合併都附上它，用來防範 BooookScore 的「實體省略／因果省略／前後矛盾」。
- 以階層合併為主（求連貫），再對「被判定為主線高光」的場景回頭從 L0 補細節（補回增量法的細節優勢）。
- 摘要後以 BooookScore 之八類錯誤做 QA 提示（該文指出評估提示須含錯誤定義與範例才準）。
- 壓縮比參考【推論】：100 萬字小說→90 分鐘稿（約 22,500 字）≈ 44:1；整季影集 10 集×45 分＝450 分→60 分鐘稿 ≈ 7.5:1（時間比）；數百話漫畫以「弧」為單位，先做 L3。

### 1.2 主線／支線取捨

**【推論】**（搜尋未得影視／小說解說專門來源，【查不到】）建議評分制，每個場景卡打分後依預算取捨：

1. **主線分**：是否推進主角核心欲望／最終衝突（0–3）。
2. **不可逆轉折**：之後劇情是否因此改變（0–3）。
3. **因果必要**：刪掉後後文是否看不懂（必留）。
4. **情緒峰值**：最高潮／最揪心／最爽處（0–2）。
5. **可評論性**：能否承載觀點、吐槽、對照（0–2），直接服務原創評論比例。
6. 其餘支線：因果必要者以一句話橋接；與主線無關者刪除（BooookScore 之「顯著性」錯誤）；一條支線若動機貫穿結局可保留成「副軸」，上限 1–2 條。
- 預算：依稿量分配到各弧，**每個弧的篇幅與其主線分總和成正比**，避免前重後輕。

### 1.3 結構、Hook 與節奏

**【事實】** YouTube 官方留存率說明：「開場（前 30 秒）」是獨立指標＝30 秒標記仍在看的比例；標題／縮圖須與實際內容相符；若 top moments 出現太晚，應把精彩內容往前移，因為觀眾數通常隨時間遞減。（<https://support.google.com/youtube/answer/9314415?hl=en>）該頁**無**任何前 30 秒流失比例的基準值。

**【事實，次級來源】** 長片 hook 建議 15–30 秒，內含大膽主張、結果預告與 open loop（<https://gotranscript.com/public/mastering-video-engagement-the-crucial-first-30-seconds-and-storytelling-techniques>，部落格性質）。另有工具頁建議 pattern interrupt 每 30–60 秒一次（<https://www.marketingmonk.so/tools/youtube-script-generator>，行銷工具頁，證據弱）。中文短影音「黃金 3 秒」把開頭鉤子分為衝突／提問／懸念（<https://www.woshipm.com/operate/6181785.html>，經驗文章）。

**【查不到】** 「每 3–5 分鐘一個小懸念」無任何來源可證；**【推論】** 此為設計參數，須以頻道留存曲線驗證（YouTube 的 dips/spikes 報表可用）。

**建議骨架（60 分鐘範例，比例可縮放）【推論】：**

| 時段 | 功能 | 備註 |
|---|---|---|
| 0:00–0:45 | Hook：最強畫面／反直覺問題／結局的一個懸念（不劇透結局，只預告代價） | 與縮圖標題承諾一致 |
| 0:45–2:30 | 設定：作品、世界觀、主角欲望，一句話承諾「看完你會知道 X」 | 同時是合理使用的「評論目的」聲明點 |
| 2:30–52:00 | 主體：分 4–6 個「弧」，每弧 8–12 分；弧內每 60–90 秒一次節奏變化（換圖組、語氣轉折、反問、數字、吐槽）；每 3–5 分鐘一個小懸念（句尾拋問題或「但他不知道的是…」） | 每弧末強 cliffhanger |
| 52:00–58:00 | 高潮與結局 | 先因果，再情緒 |
| 58:00–60:00 | 評價／主題昇華／回扣 hook（首尾呼應） | 原創觀點集中處 |

**評論與吐槽比重【推論】：** 旁白字數中劇情敘述 ≤ 70%、評論／分析／吐槽／對比 ≥ 30%；評論須針對原作「做了什麼、為何有效／無效」，不是情緒口號。台灣學者分析指出「主要在摘要情節的影片較難主張合理使用，評論、戲謔、諷刺者空間較大」（見 4.2）。

**劇本文字風格（TTS 友善）【推論】：** 單句 ≤ 30 字（超過拆句）；少用括號與英文縮寫；數字寫成口語（「三百年」而非「300年」）；專名首次出現附一句身分；避免連續四字成語堆疊；每段以句號收尾利於切分。

### 1.4 中文口播字數／時長換算

- **【實測】**（本機 edge-tts 7.2.8，194 漢字／217 字元的敘事段落，單次合成）：

| 聲音 | rate | 時長 | 漢字/分 | 字元/分 |
|---|---|---|---|---|
| HsiaoChen | -10% | 54.2 s | 215 | 240 |
| HsiaoChen | +0% | 48.8 s | 239 | 267 |
| HsiaoChen | +10% | 44.4 s | 262 | 294 |
| YunJhe | -10% | 48.9 s | 238 | 266 |
| YunJhe | +0% | 44.0 s | 265 | 296 |
| YunJhe | +10% | 40.0 s | 291 | 325 |

- 長文實測（HsiaoChen +0%，重複段落）：690 字→147.5 s（281 字元/分）；6,900 字→1,473.9 s（24.6 分；281 字元/分）。含句界事件 200 個，與句數相符。**結論：規劃用 250 字元/分偏保守（因為另需停頓），純語速約 267–296。**
- **【事實，次級】** 中文演講一般語速 200–300 字/分，標準 240–300，快 350–380（<https://uptogo.com.tw/?p=1368982>，演講教學類網頁）；換氣停頓約 0.5–1 秒、強調另加 2–3 秒（搜尋摘要，來源為 <https://miniwebtool.com/zh-tw/演講時間計算機/> 類工具頁，證據弱）。
- 公式（寫進 skill）：`預估時長(s) = 字元數 / (cpm/60) + 句數×0.30 + 段數×0.7 + 章數×1.3`（停頓值為【推論】預設，可由實測校準；cpm 依所選 TTS 實測，勿硬套）。**必須以第一次實際合成的總長回寫 cpm，再調整稿量。**
- 觀眾語速偏好【推論】：解說敘事以 rate -5%～+0% 為宜；高資訊密度段落可 +5%，不超過 +10%。
- 英文 wpm 研究（廣播 160–180 wpm）不可直接換算中文（<https://repositori.upf.edu/items/cfcf6cb5-351c-496a-8d5b-60af67ac425e>）。

---

## 2. 視覺

### 2.1 靜態圖動態化

- **【事實】** Premiere Pro、DaVinci Resolve 靜態圖預設均為 5 秒；業界並無「幾秒一張」之標準【查不到】；Ken Burns 手法之效用在於引導視線、控制節奏、增添情緒，專業作品重節制與緩動（<https://helpx.adobe.com/lt/premiere-pro/how-to/ken-burns-effect.html>、<https://frameo.ai/blog/use-ken-burns-effect-images/>）。
- **切換頻率【推論】：** 平均 4–8 秒/張；高潮段 2–4 秒；靜思／回憶段 8–12 秒（單一長鏡不宜 >12 秒）。切點對齊 TTS 句界（edge-tts SentenceBoundary 事件或 Whisper 時間戳），而非固定秒數。
- **運鏡【推論】：** 每張在 {推近, 拉遠, 左移, 右移, 上移, 下移} 擇一，**相鄰兩張不得同方向**；縮放幅度 1.00→1.06–1.15（超過 1.2 易見畫質劣化）；使用 ease-in-out；一張圖運鏡速度＝幅度/停留秒數，確保位移 < 約 2%/秒（避免暈眩）。
- **視差（2.5D）【推論】：** 將圖分前／中／後景（深度圖或手動遮罩）作不同速度位移，適用主視覺與章節卡；成本高，宜限於每章 1–3 張關鍵圖。可用 moviepy-motion-designer skill 實作。
- **ffmpeg zoompan 實務：**
  - **【事實】** zoompan 有已知抖動問題（trac #4298 仍開啟；於放大前處理可減輕）（<https://trac.ffmpeg.org/ticket/4298>、<https://lists.ffmpeg.org/pipermail/ffmpeg-devel/2020-February/257073.html>）。
  - **【實測】** 1920×1080 單張→5 秒 30fps，zoompan（`z='min(zoom+0.0008,1.15)'`，中心置中）耗時：不預放大 1.23 s；先放大 2× 1.36 s；先放大 4× 3.52 s（本機 ffmpeg 8.1.1）。**抖動肉眼品質本次未逐幀驗證**。
  - **【推論】** 預設 2× 預放大＋置中縮放；400 張圖的 4× 預放大約增加 15 分鐘，不划算。亦可改用 moviepy/Pillow 逐幀 affine 取樣以避免整數取整抖動。
- 圖來源：避免直接使用原作畫面（見第 4 節）；以原創生成插圖／示意圖／資訊圖卡（地圖、關係圖、時間軸）為主。

### 2.2 字幕規範

- **【事實】** Netflix 繁體中文字幕規範：每行 16 字、最多 2 行、成人節目 9 字/秒（兒童 7）、**只用全形標點**、不使用任何句號（行末或字幕末）、不以頓號／逗號結尾、問號必要、刪節號用 U+2026、引號用「」『』、阿拉伯數字用半形；換行偏底部較重，避免上行只剩 1–2 字。（<https://partnerhelp.netflixstudios.com/hc/en-us/articles/215994807>；簡中同為每行 16 字：<https://backlothelp.netflix.com/hc/en-us/articles/215986007-Chinese-Simplified-Timed-Text-Style-Guide>）
- 旁白實測 4.0–4.9 字/秒（見 1.4），遠低於 9 字/秒，故**解說字幕一句一行即可**，無閱讀速度壓力。
- **位置與樣式【推論】：** 底部置中、距底 8–10% 安全區；白字＋黑描邊（1080p 約 42–52 px）；避開平台 UI（YouTube 底部控制列、B 站彈幕層）；若同時有 B 站彈幕，字幕上移約 5%。
- **對時【推論】：** 優先用 TTS 句界時間戳（edge-tts `SentenceBoundary`，offset 單位為 100 ns，實測第一句 offset=1,000,000＝0.1 s）；再以 faster-whisper 抽檢；字幕最短顯示 1.0 s、最長 6 s；相鄰字幕間隔 ≥ 2 幀。
- 同時輸出 SRT（上傳 YouTube 作為可選字幕軌，利於 SEO 與無障礙）與硬字幕版（B 站／社群轉貼）。

### 2.3 章節卡（chapter card）

【推論】每章 2.5–4 秒：章序號＋章名（≤ 12 字）＋一句懸念副標；配輕音效；背景為該章關鍵圖加暗化；與 YouTube chapters 同名同序，便於對應。長片每 8–12 分鐘一張，兼具「重置注意力」功能。

---

## 3. 音訊

### 3.1 TTS 自然度（中文）

- **【事實】** edge-tts 預設 zh-TW 聲音：`zh-TW-HsiaoChenNeural`（女）、`zh-TW-YunJheNeural`（男）、另有 `zh-TW-HsiaoYuNeural`；參數 rate（如 `+0%`/`-10%`，負值於 CLI 須寫成 `--rate=-10%`）、volume、pitch（`+0Hz`）。edge-tts 專案說明稱服務只允許單一 voice 內單一 prosody，因此**不支援完整 SSML（含 `<break>`）**（搜尋摘要：<https://gitee.com/dont/edge-tts>、<https://github.com/liunix61/edge-tts>；Azure 雲端的 `<break>` 另當別論）。→ **停頓只能以「分段合成＋插入靜音」實現**【推論】。
- **斷句【推論】：** 以句號／問號／驚嘆號為主切分；長句（>30 字）在逗號處拆；每次合成請求以「一句或一小段（≤ 1,500 字元）」為單位，以便重試與句級對時。
- **停頓預設【推論】：** 句間 0.25–0.35 s；段間 0.6–0.8 s；章間 1.2–1.5 s；問句後多 0.1–0.2 s；強調處可獨立成短句。
- **標點【推論】：** TTS 以標點決定韻律——用全形「，。？！」；省略號與破折號可能被讀成長停頓或忽略，需試聽；避免「……」連用；括號內容改寫進句中。
- **數字／符號／英文【推論】：** 預處理為口語（%→百分之、年份「1995年」→「一九九五年」、單位、英文縮寫逐字母或中文譯名）；用規則表而非靠模型猜。
- **多音字【事實＋推論】：** pypinyin 可用 `heteronym=True` 列出多音字所有讀音，並以 `load_phrases_dict()`／`load_single_dict()` 建自訂詞典（<https://pypi.org/project/pypinyin/>，**目前宣告支援至 Python 3.13**，用於 3.14 前須實測）。edge-tts 無音素標註，故流程為：(1) 掃描稿件中高風險多音字（行、重、長、了、得、著、數、樂、傳、降、將、還、都、為、空、降、藏…）；(2) 對上下文可判定者放行；(3) 對 TTS 易錯詞維護「替換詞典」（如把易讀錯詞改寫成同音且不歧義的詞，或加註拆開），每次合成後以 faster-whisper 回聽比對漢字，差異標紅人工確認。本機另有 qwen3-tts／omnivoice 等 skill 可作為較可控的替代或備援聲源。
- **整體聽感【推論】：** 單一旁白長達 60+ 分鐘易疲乏，建議：(a) 每章微調 rate ±3% 與 pitch ±2Hz 作語氣變化；(b) 對話引用句可換第二聲音（注意標示，且不得仿冒真人聲音，見 4.3）；(c) 用 BGM 與音效填補章間。

### 3.2 響度

- **【事實】** YouTube 未公布官方目標響度；-14 LUFS 為觀測／慣例；真峰值建議 ≤ -1 dBTP（部分建議 -1 至 -2）；比 -14 更響不會更響，只會損失動態（<https://sounddesign.irpr.agency/guides/what-is-the-right-lufs-for-youtube-podcast-broadcast/>、<https://www.soundhouse.co.jp/en/contents/column/index?post=3560>、<https://videvo.net/blog/?p=40770> 等次級來源）。
- **【事實】** ffmpeg `loudnorm`：I 範圍 -70～-5（預設 -24）、LRA 1～50（預設 7）、TP -9～0（預設 -2）；`measured_*`＋`offset`＋`linear=true` 構成雙通道線性正規化；`linear` 於條件不足時退回 dynamic；`print_format=json` 輸出量測；官方 filters 文件：<https://ffmpeg.org/ffmpeg-filters.html#loudnorm>。官方 devel 郵件建議於 loudnorm 後加 `aresample=48000`（loudnorm 內部可能升頻至 192 kHz）（<https://ffmpeg.org/pipermail/ffmpeg-devel/2018-August/233372.html>）。
- **【實測】** 兩段式流程於本機驗證（旁白 mp3 + 合成 BGM，混音後）：
  - Pass 1：`loudnorm=I=-14:TP=-1:LRA=11:print_format=json` → input_i -19.08、input_tp -3.99、input_lra 2.80、input_thresh -29.68、target_offset 0.26。
  - Pass 2：加 `measured_I/TP/LRA/thresh`、`offset`、`linear=true`，後接 `aresample=48000` → 以 `ebur128=peak=true` 量測：**I = -14.1 LUFS、TP = -1.0 dBFS、LRA 2.1 LU**。
  - 指令骨架：
    ```
    ffmpeg -i mix.wav -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=<..>:measured_TP=<..>:measured_LRA=<..>:measured_thresh=<..>:offset=<..>:linear=true,aresample=48000" -ar 48000 out.wav
    ```
- 目標階層【推論】：旁白單軌先正規化到約 -16 LUFS，混 BGM 後整體再兩段式到 -14 LUFS／-1 dBTP。**最終比對以 ebur128 量，不以耳朵。**
- 長片注意【推論】：60–120 分鐘單檔直接量；分段合成後各段不要各自 normalize（會造成段間響度跳動），應全片混完後再一次正規化。

### 3.3 BGM 避讓（ducking）

- **【事實】** ffmpeg `sidechaincompress`：threshold 預設 0.125（範圍 0.00097563–1）、ratio 預設 2（1–20）、attack 預設 20 ms（0.01–2000）、release 預設 250 ms（0.01–9000）、makeup 1–64、level_sc 1–64、detection rms/peak（<https://ffmpeg.org/ffmpeg-filters.html#sidechaincompress>）。FFmpeg-user 郵件另提示多級串接時音質需耳測（<https://lists.mplayerhq.hu/pipermail/ffmpeg-user/2021-July/053266.html>）。
- **【實測】** 以下濾鏡圖於 ffmpeg 8.1.1 執行成功（BGM 為合成正弦波，**聽感品質未評估**）：
  ```
  [0:a]aresample=48000,asplit=2[vo][sc];
  [1:a]aresample=48000,volume=-18dB[bg];
  [bg][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400:makeup=1[duck];
  [vo][duck]amix=inputs=2:duration=first:normalize=0[mix]
  ```
- 建議起始值【推論】：BGM 基準比旁白低 18–22 dB；有人聲時再壓 8–12 dB（ratio 6–10）；attack 15–30 ms、release 300–600 ms；章節卡／過場無旁白時 BGM 可拉回基準（用 `volume` 包絡或 sidechain 自然回升）。
- BGM 來源：自製（suno-song-creator skill）、YouTube Audio Library 或明確授權者；**不得使用原作配樂／OP/ED**；保留授權記錄（見 4.4）。YouTube 說明：Content ID 無法判斷合理使用，數秒即可觸發聲明並阻擋營利（<https://support.google.com/youtube/answer/9783148?hl=en>）。

---

## 4. 平台規範與版權風險

> 以下為研究整理，非法律意見。YouTube 官方頁明言其無法判定合理使用、不調解版權爭議。

### 4.1 YouTube

**重複使用內容（reused content）與 inauthentic content（官方頁：<https://support.google.com/youtube/answer/1311392?hl=en>）【事實】**
- 2025-07-15 更新：把「repetitious content」更名為「inauthentic content」，涵蓋重複／量產內容；**重複使用內容政策未變**，仍審視評論、片段、合輯、反應影片等（<https://ppc.land/youtube-clarifies-inauthentic-content-policy-changes/>、官方頁）。
- 重複使用：未加入「重大原創評論、實質修改、教育或娛樂價值」而重製他人內容，不得營利；檢驗標準＝觀眾能分辨你的版本與原版有實質差異。
- 允許：針對原作加入評論的反應／影評；有敘事與評論的剪輯。不允許：幾乎無敘事的片段拼接；下載後未實質修改；只變調變速的歌曲；只有非語言反應。
- **作者許可不免除審查**；此政策與版權執法分開；政策以**整個頻道**為審查單位，若審查員無法明確看出內容是你製作，可能整頻道失去營利。
- **inauthentic（量產）風險項（與本流程高度相關）：** 官方頁列為不允許者包含「圖片幻燈片、套版故事線、或幾乎無敘事／價值的捲動文字」、「基於泛用範本、缺乏創作者自身觀點的 AI 內容」；重複的情境、同樣結果、影片間變化極小。允許：固定的片頭片尾（只要主體不同）。垃圾內容政策亦禁止以 AI 大量產出相似內容（<https://support.google.com/youtube/answer/2801973?hl=en>，該頁實際為 Spam policy）。
  → **對 AI 靜態圖＋TTS 流水線的含義【推論】：** 每支片須具備可辨識的獨有觀點、結構與敘事差異；避免所有影片套同一組背景音樂＋同一種圖風＋同一句型；建議加入人工審稿與個人化內容（真人露出／真人聲音／頻道固定評論欄目）。

**AI／合成內容揭露（官方頁：<https://support.google.com/youtube/answer/14328491?hl=en>）【事實】**
- 須揭露：逼真的、以 AI 生成或實質修改的內容——讓真人看似說／做了未做之事、改動真實事件或地點的影像、生成未曾發生之逼真場景、以音樂為主體的 AI 音樂。
- **無須揭露：** 明顯非寫實（如獨角獸奇幻世界）、純美化／色彩／特效、**製作輔助（腳本、縮圖）**、字幕、升頻與音訊修復、發想、**複製自己的聲音做旁白**、遊戲畫面。
- 揭露方式：YouTube Studio 上傳流程「Attributes」→「AI use」選 Yes/No。標籤位置：寫實內容可能顯示於播放器，非寫實／動畫顯示於展開的說明欄；YouTube 可能依 C2PA 中繼資料或偵測自動加標；長期不揭露可能被人工加標、下架或被停權 YPP。揭露**不影響**觀看範圍與營利資格。
- **對本流程的含義【推論】：** 動畫／插畫風格圖像＋一般 TTS 旁白通常屬不須揭露；但若圖像為「逼真」且描繪真實人物／真實事件（如歷史 recap 用寫實 AI 生成人物影像）、或使用仿冒他人聲音，則須勾選 Yes。保守做法：**凡使用 AI 生成逼真圖像一律勾 Yes**，並在說明欄寫明「本片圖像由 AI 生成、旁白為合成語音」。（次級來源對生效日有分歧，一說 2024-03 工作室開關上線、一說 2025-05-21 生效，以官方頁為準。）

**合理使用四要素（美國法 17 U.S.C. §107）【事實】**
1. 使用之目的與性質（商業／非營利教育；是否具轉化性）；
2. 著作性質（創作性作品，如小說、電影，較不利；事實性作品較有利）；
3. 使用之質與量及占整體比例（即使少量，若取其「核心」亦不利）；
4. 對著作潛在市場或價值之影響（是否替代原作）。
- 來源：<https://www.copyright.gov/fair-use/>。該頁明言：**無任何保證安全的固定百分比或字數**；轉化性使用＝加入新內容、不同目的或性質且不替代原作。
- YouTube 官方：標註作者來源、「不侵權」聲明、把影片稱為「娛樂」皆無法自動構成合理使用；Content ID 是自動系統，不能判斷合理使用；可走爭議／申訴／DMCA 反通知（<https://support.google.com/youtube/answer/9783148?hl=en>）。
- 歐盟僅有列舉例外（引用、評論、諷刺等），其他地區為 fair dealing，各異。

### 4.2 臺灣／中國的法律脈絡（因目標觀眾為繁中）

**臺灣【事實】**
- 著作權法第 65 條：合理使用不構成侵害；判斷基準四項：利用目的與性質（含商業／非營利教育）、著作性質、所利用之質量及其占整體之比例、對潛在市場與現在價值之影響（<https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0070017&flno=65>）。
- 第 52 條：為報導、評論、教學、研究或其他正當目的之必要，在合理範圍內得引用已公開發表之著作；需註明出處（第 64 條）。張中信教授分析「X 分鐘看完電影」：主要在摘要情節者較難主張合理使用；評論、戲謔、諷刺者空間較大；不以是否合法來源為要件（<https://www.inside.com.tw/article/9160-copyrightnote-amogood>）。
- 谷阿莫案：2017 年被片商提告、被檢察官起訴；另一分析稱此類影片涉及重製與改作兩層（<https://technews.tw/2017/04/30/amogood-and-copyright-issues/>、<https://ah.lib.nccu.edu.tw/handle/140.119/126611?mode=full>）。**最終判決結論查不到。**
- 重點：**以「摘要劇情」為主體的小說／影視解說，是風險最高的類型（改作權、重製權）。** 小說解說尤其接近「用自己的話重述全書情節」。

**中國大陸【事實，媒體整理】**
- 「圖解電影」案：一審北京互聯網法院認定侵害信息網路傳播權，判賠 3 萬元（原告索賠 50 萬）；法院認定被告截取 382 幅畫面，屬具獨創性的表達；二審維持，並指改變作品表現形式不等於不使用作品（<https://www.ithome.com/0/496/307.htm>、<https://www.thepaper.cn/newsDetail_forward_7559494>；僅新聞整理，未核對判決書全文）。
- 2021-04 多家影視公司與平台聯合聲明反對未經授權的剪輯、切條、搬運（<https://www.chinanews.com.cn/sh/2023/12-06/10123244.shtml>）。
- 判斷常見標準：是否對原作形成「實質性替代」（<https://www.thepaper.cn/newsDetail_forward_13627665>，媒體報導）。

### 4.3 Bilibili

- **【事實，媒體轉述；官方原文未取得】** 《人工智能生成合成内容标识办法》（國家網信辦等四部門）自 2025-09-01 施行，要求對 AI 生成的文本、圖片、音訊、視頻等加顯式與隱式標識。B 站宣布 2025-09-20 上線「創作者聲明」功能：投稿含 AI 內容須聲明（如「該視頻使用人工智能合成技術」）；轉載須在投稿頁選「轉載」並附來源；聲明與內容不符社區可修改；B 站投稿後左下角與簡介會顯示 AI 標示。（<https://m.thepaper.cn/newsDetail_forward_31523045>、<https://www.ithome.com/0/879/622.htm>、<https://news.bjd.com.cn/2025/08/31/11290869.shtml>；平台未主動標註 AI 者，部分平台會限流、下架或封號。）
- **【事實，媒體轉述】** 《bilibili創作公約2.0》：未經著作權人許可不得傳播／出售已公開或未公開的視聽作品（動畫、影視、音樂、遊戲等）；違規內容減少推薦或退回，嚴重者封號（<https://www.ifanr.com/minapp/1414055>）。創作激勵只適用「自制」影片，番劇、廣告、放映廳類暫不享受收益（B 站創作激勵頁，經搜尋摘要）。
- 【查不到】B 站對「自制」與「轉載」的官方判定細則、解說類內容的專門規範（已嘗試以官方頁搜尋；36kr 頁面抓取失敗）。**上傳 B 站前須由人工讀取最新創作公約與創作者聲明頁。**
- 大陸 AIGC 標識：即使 TTS 與插畫為通用風格，也**建議一律勾選「使用 AI 合成」**【推論，保守】。

### 4.4 降低版權風險的實務清單（【推論】，合併上述事實）

1. **評論先行：** 每章至少一段觀點／分析／對比；全片評論字數 ≥ 30%；片頭以「評論目的」定調（但「聲明」本身不構成合理使用）。
2. **不替代原作：** 摘要到「足以討論，但不足以代替閱讀」——保留關鍵反轉的細節與文字魅力給原作；結局可「評價式」呈現而非逐段復述；片尾導流到正版（連結／書名／作者）。對連載未完或正在販售的原作尤須謹慎。
3. **素材轉化：** 不用原圖、原聲、原配樂；以原創（或自有授權）插畫、地圖、關係圖取代；若必須引用原圖，僅一張靜態、註明出處、為評論所必要。
4. **不引用大段原文：** 逐字引文 ≤ 兩三句（短語級）；其餘改寫。
5. **標註來源與作者：** 片頭與說明欄寫明作品名、作者、出版方（臺灣法第 64 條）。
6. **素材來源紀錄：** 每支影片維護 `sources.json`（見 4.5）。
7. **避開高風險標的：** 近期熱門、仍在院線／連載、版權方積極維權者；偏向已進入公共領域（如古典文學、歷史）或取得授權者。
8. **頻道層級防量產：** 不同影片變換結構與觀點；保留人工審稿紀錄；定期檢視 YouTube 「重複使用／inauthentic」政策頁。
9. **AI 揭露：** YouTube Studio「AI use」；B 站創作者聲明；說明欄文字揭露。
10. **爭議處理預案：** 保存底稿、版本、評論稿，以應 Content ID 聲明申訴。

### 4.5 流程檢查點（供 skill 寫入）

| 檢查點 | 時機 | 內容 | 不通過則 |
|---|---|---|---|
| CP-1 立項 | 選題後 | 原作版權狀態、是否仍在銷售／連載、授權可能；風險等級 | 換題或降級為「評論主導」格式 |
| CP-2 稿件 | 劇本完成 | 評論字數比 ≥ 30%、逐字引文 ≤ 2–3 句、每章有觀點段、無「純複述」章 | 退回改寫 |
| CP-3 素材 | 出圖／選樂後 | `sources.json` 完整、無原作畫面／原聲、BGM 授權可查 | 替換素材 |
| CP-4 AI 揭露 | 上傳前 | 圖像是否逼真、是否涉真人／真實事件、是否仿聲；決定 YT「AI use」與 B 站聲明 | 補勾選 |
| CP-5 頻道健檢 | 每 5 支片 | 與前作相似度（結構／圖風／句型／BGM）、獨有觀點 | 調整模板 |
| CP-6 上架後 | 發佈後 7 日 | 版權聲明、留存曲線、評論 | 申訴／修片 |

`sources.json` 欄位建議：`work{title,author,publisher,type,year}`、`license_status`、`assets[{id,type,origin(generated|self|licensed|public_domain),tool,prompt_ref,license_url,used_at}]`、`bgm[{title,source,license_url}]`、`quotes[{text,source,len}]`、`ai_disclosure{images,voice,music}`、`commentary_ratio`、`checked_by/at`。

---

## 5. 長片製作工程

### 5.1 分段與資料模型

【推論】以「章 → 段 → 句」三級切分，所有工件以內容雜湊（SHA-256）為 key 做快取：

```
script.json
 chapters[] { id, title, hook_line, paragraphs[] { id, sentences[] { id, text, tts_text, image_ref, motion } } }
```
- `tts_text`：經預處理（數字口語化、多音字替換、標點正規化）的文字；與 `text`（字幕顯示用）分開存。
- 每句／每段合成一個音檔；檔名含雜湊：`audio/{chapter}/{para}-{sha8}.wav`；稿件改一句只重合成那一句。

### 5.2 批次 TTS 與失敗重試

- **【實測】** edge-tts 單次請求可處理長文：690 字 8 s（~18× 即時）、2,760 字 32 s、6,900 字 79 s（輸出 24.6 分鐘音訊），句界事件數量正確。→ 單請求可行，**但失敗時需重做整段**，故仍建議每請求 ≤ 1,500 字元（約 5 分鐘音訊、約 20 s 實時）。
- **【實測】** 本機曾於同一 session 第一次連續呼叫出現 `AttributeError: module 'aiohttp' has no attribute 'ClientTimeout'`，隨即重跑成功，原因未查明（疑與環境載入有關）；**因此重試機制必要**。重試建議【推論】：最多 3 次、指數退避 2/4/8 s + 抖動；連續失敗改用備援聲源（qwen3-tts／omnivoice）並在 manifest 記錄 `engine` 以免風格混雜。
- 並行度【推論】：同時 2–4 個請求；服務端限流時降為 1；每個請求以 `asyncio.wait_for` 設逾時（如 120 s）。
- 完成度檢查【推論】：合成後以 ffprobe 取時長，若 時長/字元 落在期望區間 [0.8×, 1.3×] 之外（可能被截斷或亂讀）視為失敗重做；靜音偵測（`silencedetect`）排除空檔。
- 回聽驗證【推論】：抽樣（或全量，GPU 3060 Ti 可負擔）以 faster-whisper 轉寫並與 `tts_text` 比對，字元差異 > 5% 之句標記複聽。

### 5.3 對時與時間軸

- **句界時間戳**：edge-tts `stream()` 以 `boundary="SentenceBoundary"` 回傳 `offset`/`duration`（100 ns 單位）【實測】；每句獨立合成時則以 ffprobe 時長為準。
- **全域時間軸計算【推論】：** 
  `t_start(sentence) = Σ 前面所有 (音檔實長 + 其後停頓)`，停頓以靜音檔插入；用解碼後 PCM 的取樣數（48 kHz）累加，**不要用 MP3 時長累加**（MP3 編碼延遲與填充會讓長片累積漂移）。
- 畫面事件（換圖、運鏡、章節卡）全部由時間軸派生，而非獨立計時；影片總長＝音訊總長＋片頭尾。
- 校驗【推論】：輸出後 ffprobe 比對影片音軌長度與時間軸總長，誤差 > 0.1 s 失敗；每章邊界抽取該秒前後 2 s 視聽確認。

### 5.4 影片組裝（長片）

【推論】
- 逐章渲染成中間檔（章 mp4 + 章 wav），最後以 concat demuxer 無損拼接，失敗只重做該章；中間檔採一致編碼參數（1080p30、libx264 crf 18–20、yuv420p、AAC 48 kHz）。
- 全片音訊混完再整體兩段式 loudnorm（3.2），最後把成音 mux 回視頻（視頻 `-c copy`）。
- 渲染時間參考：本機單張 5 秒 Ken Burns 約 1.2–1.4 s（2× 預放大）【實測】，故 1,000 張約 20–25 分鐘；可章級並行。
- GPU 編碼可選 `h264_nvenc`（RTX 3060 Ti）加速，【未驗證】本流程中的畫質差異。

### 5.5 YouTube chapters 時間軸產生

- **【事實】** 規則：寫在說明欄；每行「時間 標題」；第一個必須為 00:00；至少 3 個；遞增；每章 ≥ 10 秒；手動章節覆蓋自動章節（<https://support.google.com/youtube/answer/9884579?hl=en>）。次級來源補充：任一行格式錯誤可能使整串失效；<1 小時用 MM:SS，≥1 小時用 H:MM:SS（<https://www.storyblocks.com/resources/tutorials/how-to-add-chapters-to-youtube-video>、<https://gyre.pro/blog/youtube-video-chapters-how-to-add-them-why-they-increase-views>）。
- **產生【推論】：** 章起點＝時間軸中該章第一句 `t_start`（若有章節卡則取章節卡起點）；四捨五入到整秒（向下取整）；標題 ≤ 40 字且同章節卡；產生後驗證四項規則再輸出 `chapters.txt`；同時輸出 `chapters.json`（含毫秒）供 B 站／剪映使用。
- 長片 HH:MM:SS 格式一律統一（≥ 1 小時片中所有行都用 H:MM:SS 較穩）。

### 5.6 產出物與可重現性【推論】

`manifest.json`：版本、模型／聲音、rate/pitch、cpm 實測、各句雜湊、重試次數、錯誤、最終 LUFS/TP、總長；`sources.json`（4.5）；`chapters.txt`；`subs.srt`；`report.md`（檢查點通過記錄）。

---

## 6. 檢查清單（可直接貼入 skill）

### 6.1 劇本
- [ ] 已建 story bible（人物／地點／時間線／因果帳本／伏筆）
- [ ] 分層摘要 L1–L4 皆為結構化輸出，章摘要通過八類錯誤 QA（實體／事件／因果省略、不連貫、顯著性、語言、矛盾、重複）
- [ ] 每場景有主線分；支線有取捨記錄；各弧篇幅與主線分成正比
- [ ] 前 45 秒含 hook 且與標題縮圖承諾一致，不劇透結局
- [ ] 每 60–90 秒一次節奏變化，每 3–5 分鐘一個小懸念（參數可調）
- [ ] 評論／分析字數 ≥ 30%，每章 ≥ 1 段觀點
- [ ] 單句 ≤ 30 字，數字口語化，專名首次附註
- [ ] 稿量符合 片長×cpm（實測值回寫後再校），誤差 ±5%

### 6.2 視覺
- [ ] 每張 4–8 秒、切點對齊句界；相鄰運鏡方向不同
- [ ] 縮放 ≤ 1.15、預放大 ≥ 2×（避免 zoompan 抖動）
- [ ] 字幕每行 ≤ 16 字、≤ 2 行、全形標點、無句號
- [ ] 章節卡 2.5–4 秒，與 chapters 同名同序

### 6.3 音訊
- [ ] 句間／段間／章間靜音依預設插入
- [ ] 多音字掃描＋回聽比對通過
- [ ] BGM 低 18–22 dB，人聲段再壓 8–12 dB
- [ ] 全片兩段式 loudnorm 後 ebur128 實測 I ∈ [-14.5, -13.5]、TP ≤ -1.0
- [ ] 取樣率 48 kHz；無截波

### 6.4 平台／版權
- [ ] CP-1～CP-6 皆通過並記錄
- [ ] 無原作原聲、原畫面（或例外已記錄）；BGM 授權可查
- [ ] `sources.json` 完整
- [ ] YouTube「AI use」判定已做；B 站創作者聲明已勾；說明欄 AI 與來源揭露
- [ ] 說明欄附作品與作者資訊、導流正版
- [ ] 與前 4 支片的結構／圖風／句型差異檢查（防 inauthentic）

### 6.5 工程
- [ ] 句級雜湊快取；重試 ≤ 3 次含退避；備援聲源已記錄
- [ ] 時間軸以 PCM 取樣數累加，成片音長與時間軸誤差 ≤ 0.1 s
- [ ] chapters.txt 通過四項規則驗證（≥3、首 00:00、遞增、每章 ≥10 s）
- [ ] manifest.json 與 report.md 已生成

---

## 7. 來源索引

官方／一手：
- YouTube 重複使用與 inauthentic 內容：<https://support.google.com/youtube/answer/1311392?hl=en>
- YouTube Spam policy：<https://support.google.com/youtube/answer/2801973?hl=en>
- YouTube AI 揭露：<https://support.google.com/youtube/answer/14328491?hl=en>
- YouTube 章節：<https://support.google.com/youtube/answer/9884579?hl=en>
- YouTube 合理使用與 Content ID：<https://support.google.com/youtube/answer/9783148?hl=en>
- YouTube 留存率：<https://support.google.com/youtube/answer/9314415?hl=en>
- 美國版權局合理使用：<https://www.copyright.gov/fair-use/>
- 臺灣著作權法第 65 條：<https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0070017&flno=65>
- Netflix 繁中字幕規範：<https://partnerhelp.netflixstudios.com/hc/en-us/articles/215994807>
- FFmpeg filters：<https://ffmpeg.org/ffmpeg-filters.html>
- FFmpeg loudnorm 雙通道範例（devel）：<https://ffmpeg.org/pipermail/ffmpeg-devel/2018-August/233372.html>
- zoompan 抖動：<https://trac.ffmpeg.org/ticket/4298>
- 論文：<https://arxiv.org/abs/2109.10862>、<https://arxiv.org/html/2310.00785v4>
- pypinyin：<https://pypi.org/project/pypinyin/>

二手／次級（證據較弱，已於文中標註）：
- 台灣法律分析：<https://www.inside.com.tw/article/9160-copyrightnote-amogood>、<https://technews.tw/2017/04/30/amogood-and-copyright-issues/>
- 大陸案例與 B 站：<https://www.ithome.com/0/496/307.htm>、<https://www.thepaper.cn/newsDetail_forward_7559494>、<https://www.chinanews.com.cn/sh/2023/12-06/10123244.shtml>、<https://m.thepaper.cn/newsDetail_forward_31523045>、<https://www.ithome.com/0/879/622.htm>、<https://news.bjd.com.cn/2025/08/31/11290869.shtml>、<https://www.ifanr.com/minapp/1414055>
- 響度：<https://sounddesign.irpr.agency/guides/what-is-the-right-lufs-for-youtube-podcast-broadcast/>、<https://www.soundhouse.co.jp/en/contents/column/index?post=3560>
- 語速與 hook：<https://uptogo.com.tw/?p=1368982>、<https://gotranscript.com/public/mastering-video-engagement-the-crucial-first-30-seconds-and-storytelling-techniques>、<https://www.woshipm.com/operate/6181785.html>
- Ken Burns：<https://helpx.adobe.com/lt/premiere-pro/how-to/ken-burns-effect.html>、<https://frameo.ai/blog/use-ken-burns-effect-images/>

## 8. 未驗證與限制
- 【查不到】：小說／漫畫解說專門的壓縮比與主線取捨文獻；「每 3–5 分鐘小懸念」的實證；「原創評論 ≥ 30%」之任何官方比例（皆為本文設計參數）；B 站官方創作公約全文與「自制／轉載」判定細則；谷阿莫案最終判決。
- 實測僅限本機 edge-tts 單一樣本（194 漢字敘事段）與長文重複段落；語速會隨文本類型變動，上線前須以實際稿件重測。
- ffmpeg 濾鏡圖僅驗證可執行與響度指標；BGM 為合成正弦波，ducking 聽感、zoompan 抖動肉眼品質**未驗證**。
- 多音字處理流程為設計；pypinyin 與 Python 3.14 相容性、替換詞典效果未實測。
- YouTube AI 揭露生效日次級來源互相矛盾，以官方頁為準；政策隨時間變動。
- 法律部分為資訊整理，非法律意見；不同司法管轄區結論可能不同。
