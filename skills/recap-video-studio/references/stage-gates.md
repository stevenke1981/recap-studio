# 階段閘門與可貼式檢查（recap-video-studio 附錄）

約定：`S=/d/recap-studio/scripts`、`P=/d/recap-studio/projects/<slug>`（Git Bash）。腳本參數以 `python <script> -h` 為準。所有 `python -c` 都是唯讀檢查。

## 1. 階段探針（不知做到哪時）
```bash
python - "$P" <<'PY'
import sys, json
from pathlib import Path
p = Path(sys.argv[1])
def has(rel, glob=False):
    q = p / rel
    return any(q.parent.glob(q.name)) if glob else q.exists() and (q.stat().st_size > 0 if q.is_file() else True)
steps = [
 ("S0 project.json",         has("project.json")),
 ("S1 outline",              has("01_outline/outline.md")),
 ("S2 script",               has("02_script/script.md")),
 ("S3a shots.json",          has("03_storyboard/shots.json")),
 ("S4 audio manifest",       has("05_audio/manifest.json")),
 ("S4 full.srt",             has("06_subs/full.srt")),
 ("S3b images (any)",        has("04_assets/images/*.*", glob=True)),
 ("S5 preview.mp4",          has("07_render/preview.mp4")),
 ("S5 final.mp4",            has("07_render/final.mp4")),
 ("S6 chapters.txt",         has("08_publish/chapters.txt")),
 ("S6 qa_report.md",         has("08_publish/qa_report.md")),
 ("S6 description.md",       has("08_publish/description.md")),
]
for name, ok in steps:
    print(("[x] " if ok else "[ ] ") + name)
PY
```
`[x]` 僅表示檔案存在，**不表示內容通過閘門**；以對應階段之閘門指令確認。最後一個 `[x]` 的下一階段即續作起點；人工閘門已否通過，讀 `$P/00_source/review_log.md`。

## 2. 時間軸總長與語速回寫（S4）
```bash
python - "$P" <<'PY'
import sys; sys.path.insert(0, r"<repo>\scripts")
from pathlib import Path
from recap_common import load_project, load_shots, load_audio_manifest, build_timeline
p = Path(sys.argv[1]); c = load_project(p); s = load_shots(p)
t = build_timeline(c, s, load_audio_manifest(p))     # 缺音檔會 KeyError：先跑 tts_batch
total = t[-1].end
chars = sum(len(g["text"]) for h in s["chapters"] for g in h["segments"])
voice = sum(float(load_audio_manifest(p)["segments"][g["id"]]["duration"]) for h in s["chapters"] for g in h["segments"])
print(f"timeline {total/60:.2f} min (target {c['target_minutes']}), chapters {len(s['chapters'])}")
print(f"chars {chars}, measured {chars/(voice/60):.0f} chars/min of pure speech, planning {chars/(total/60):.0f} chars/min incl. pauses")
print("OK" if abs(total/60 - c["target_minutes"]) <= 0.05 * c["target_minutes"] else "OFF (>5%): 回 S2 增刪稿，或微調 tts_rate")
PY
```
章均長度、單段長度分布另可查：`shots.json` 中 `text` 長度 ÷ 4.4 字／秒 ≈ 該段秒數，> 12 秒者 S3b 需加圖。

## 3. 各階段閘門表
| 階段 | 機器閘門（皆須 exit 0／無 FAIL） | 人工／agent 審核 |
|---|---|---|
| S0 | project.json 欄位檢查；9 個子目錄；`sources.csv` 有表頭 | H1：題材、風險等級、片長（CP-1） |
| S1 | `outline.md` 非空；標題結構依 recap-source-digest | H2：logline、轉折、主線取捨 |
| S2 | `script_to_shots.py $P` 成功；字元數在預算 ±5% | H3 全稿；評論比 ≥ 門檻、每章觀點段、引文 ≤ 2–3 句（CP-2）；reviewer agent 初審 |
| S3a | `script_to_shots.py` 成功；每段 `image_prompt` 非空；`motion`∈契約集合 | H4a：3–5 張風格樣張 |
| S4 | `tts_batch.py $P` exit 0；`build_subs.py $P` exit 0；`qa_check.py $P --pre-render` 無 FAIL；時間軸與目標差 ≤ 5% | H5：試聽 ch01＋高密度章 |
| S3b | `qa_check.py $P --pre-render`：無「缺圖」FAIL、無「佔位圖」WARN；sources 檢查 PASS | H4b：抽檢 10% 圖（CP-3） |
| S5 | `render.py $P` 成功；`qa_check.py $P`：final 時長差 < 0.5 s、響度 ±1 LU | H6：看 preview 與 final 抽樣 |
| S6 | `make_chapters.py $P` 成功（無「only N chapters」警告）；`qa_check.py $P` exit 0；`description.md` 存在 | H7：AI 揭露、版權、說明欄（CP-4）；主人自行發布 |

S3a 的 image_prompt 檢查：
```bash
python - "$P" <<'PY'
import sys, json
from pathlib import Path
s = json.loads((Path(sys.argv[1]) / "03_storyboard/shots.json").read_text(encoding="utf-8"))
segs = [g for h in s["chapters"] for g in h["segments"]]
bad = [g["id"] for g in segs if not g.get("image_prompt", "").strip()]
print(f"{len(segs)} segments, {len(bad)} without image_prompt", bad[:10])
raise SystemExit(1 if bad else 0)
PY
```

## 4. CP 檢查點對照（研究 `02-genre-craft.md` §4.5）
| CP | 對應階段 | 內容 |
|---|---|---|
| CP-1 立項 | S0／H1 | 版權狀態、是否仍銷售／連載、風險等級 |
| CP-2 稿件 | S2／H3 | 評論比、引文長度、每章觀點、無純複述章 |
| CP-3 素材 | S3b／H4b | sources.csv 完整、無原作畫面／原聲、BGM 授權 |
| CP-4 AI 揭露 | S6／H7 | 圖像逼真度、真人／真實事件、仿聲；YT AI use、B 站聲明 |
| CP-5 頻道健檢 | 每 5 支片 | 與前作相似度（結構／圖風／句型／BGM） |
| CP-6 上架後 | 發佈後 7 日 | 版權聲明、留存曲線、評論 |

## 5. review_log.md 範本（約定，非契約檔）
```
日期,閘門,結論,簽核人,備註
2026-10-12,H1,通過（風險 A）,主人,公版《聊齋志異》
2026-10-13,H3,退回,主人,第 4 章評論不足
```
