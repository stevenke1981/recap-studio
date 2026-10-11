"""Script budget / commentary / TTS-lint report for 02_script/script.md.

Usage:
    python script_stats.py <project_dir | path/to/script.md> [--minutes N] [--cpm 250]
                           [--max-sentence 30] [--min-commentary 0.30]

Conventions (see SKILL.md):
  * ``<!-- note: 評論 -->`` on its own line before a paragraph tags it as commentary;
    ``<!-- note: 增寫 -->`` tags dramatised additions (public-domain works).
  ``評論×3`` tags the next three paragraphs.
  * Counting follows script_to_shots.py: narration chars = characters in paragraphs.
Exit code 1 when a hard check FAILs (budget gate, markdown leakage, over-long sentence).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from recap_common import load_project  # noqa: E402
from script_to_shots import CHARS_PER_MINUTE, split_sentences  # noqa: E402

COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)
TAG_RE = re.compile(r"^\s*note\s*:\s*(評論|增寫)(?:\s*[x×*]\s*(\d+))?")
IMAGE_RE = re.compile(r"^\s*image\s*:", re.IGNORECASE)
MD_LEAK_RE = re.compile(r"^(\s*[-*>|]\s|\s*\d+\.\s|\s*-{3,}\s*$|\s*`{3})|\*\*|`")
FINAL_PUNCT = "。！？…；"
CLOSERS = "」』”’）)\"'】》"
LINT_RULES = (
    ("數字", re.compile(r"[0-9０-９]+"), "阿拉伯數字，改寫為中文數字"),
    ("英文", re.compile(r"[A-Za-z]+"), "英文字母，改中譯或登記讀音"),
    ("括號", re.compile(r"[（(\[【][^）)\]】]*[）)\]】]?"), "括號內容，改寫進句中"),
    ("破折號", re.compile(r"—+|--"), "破折號 TTS 讀法不穩"),
    ("半形標點", re.compile(r"[,.;:?!]"), "半形標點，改全形"),
    ("句中刪節號", re.compile(r"…+(?![」』”’）)\"'】》]*\s*$)"), "「…」會被視為句末而切 segment"),
)


def tokenize(raw: str):
    """Yield (kind, payload): 'chapter', 'tag', 'image', 'text'; blank lines flush paragraphs."""
    pos = 0
    pieces = []
    for m in COMMENT_RE.finditer(raw):
        pieces.append(("text", raw[pos : m.start()]))
        body = m.group(1)
        tag = TAG_RE.match(body)
        pieces.append(("tag", (tag.group(1), int(tag.group(2) or 1))) if tag else ("image" if IMAGE_RE.match(body) else "skip", ""))
        pos = m.end()
    pieces.append(("text", raw[pos:]))
    return pieces


def parse(raw: str) -> list[dict]:
    chapters: list[dict] = []
    lines: list[str] = []
    pending_tag, pending_n = "", 0

    def chapter() -> dict:
        if not chapters:
            chapters.append({"title": "開場", "paras": [], "images": 0})
        return chapters[-1]

    def flush() -> None:
        nonlocal pending_tag, pending_n
        if lines:
            chapter()["paras"].append({"lines": lines[:], "tag": pending_tag})
            lines.clear()
            pending_n -= 1
            if pending_n <= 0:
                pending_tag, pending_n = "", 0

    for kind, payload in tokenize(raw):
        if kind == "tag":
            flush()
            pending_tag, pending_n = payload
        elif kind == "image":
            flush()
            chapter()["images"] += 1
        elif kind == "text":
            for line in payload.splitlines():
                s = line.strip()
                if not s:
                    flush()
                elif s.startswith("## "):
                    flush()
                    chapters.append({"title": s[3:].strip(), "paras": [], "images": 0})
                elif re.match(r"#+(\s|$)", s):
                    flush()
                else:
                    lines.append(s)
    flush()
    return [c for c in chapters if c["paras"]]


def join(lines: list[str]) -> str:
    return "".join(lines)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="script.md budget / commentary / TTS lint")
    ap.add_argument("target", help="project dir or script.md path")
    ap.add_argument("--minutes", type=float, help="target minutes (default: project.json target_minutes)")
    ap.add_argument("--cpm", type=float, default=250, help="planning chars/min (default 250)")
    ap.add_argument("--max-sentence", type=int, default=30)
    ap.add_argument("--min-commentary", type=float, default=0.30)
    args = ap.parse_args()

    target = Path(args.target)
    cfg = load_project(target if target.is_dir() else target.parents[1])
    script = target / "02_script" / "script.md" if target.is_dir() else target
    chapters = parse(script.read_text(encoding="utf-8"))
    if not chapters:
        print("FAIL no narration found")
        return 1
    minutes = args.minutes or float(cfg["target_minutes"])
    seg_max = int(cfg["segment_max_chars"])
    max_para = 2 * seg_max
    fails: list[str] = []
    warns: list[str] = []

    rows, total, total_c = [], 0, 0
    for ci, ch in enumerate(chapters, 1):
        chars = sum(len(join(p["lines"])) for p in ch["paras"])
        com = sum(len(join(p["lines"])) for p in ch["paras"] if p["tag"] == "評論")
        rows.append((ci, ch["title"], chars, com, ch["images"]))
        total += chars
        total_c += com
        if com == 0:
            warns.append(f"ch{ci:02d} 無評論段（每章須 >= 1 段）")
        if len(ch["title"]) > 12:
            warns.append(f"ch{ci:02d} 章名 {len(ch['title'])} 字 > 12（章節卡／chapters 用）")

    print(f"{'ch':>4} {'chars':>6} {'min@%d' % args.cpm:>8} {'share':>6} {'評論%':>6} {'img':>4}  title")
    for ci, title, chars, com, imgs in rows:
        print(f"{ci:>4} {chars:>6} {chars / args.cpm:>8.1f} {chars / total:>6.0%} "
              f"{(com / chars if chars else 0):>6.0%} {imgs:>4}  {title}")
    est270 = total / CHARS_PER_MINUTE
    lo, hi = minutes * 0.9, minutes * 1.1
    print(f"\ntotal chars {total} | target {minutes:g} min -> budget {minutes * args.cpm:.0f} chars @{args.cpm:g}")
    print(f"planning est. {total / args.cpm:.1f} min (@{args.cpm:g}); "
          f"script_to_shots est. {est270:.1f} min (@{CHARS_PER_MINUTE}); gate window {lo:.1f}-{hi:.1f} min")
    if not lo <= est270 <= hi:
        fails.append(f"script_to_shots 估算 {est270:.1f} 分不在目標 {minutes:g} 分 ±10%")
    plan_dev = total / args.cpm / minutes - 1
    if abs(plan_dev) > 0.05:
        warns.append(f"稿量偏離規劃預算 {plan_dev:+.1%}（建議 ±5% 內）")
    ratio = total_c / total
    print(f"commentary (tagged 評論): {total_c} chars = {ratio:.0%} (min {args.min_commentary:.0%})")
    if ratio < args.min_commentary:
        fails.append(f"評論比重 {ratio:.0%} < {args.min_commentary:.0%}（含未標記者請補標記）")

    for ci, ch in enumerate(chapters, 1):
        for pi, p in enumerate(ch["paras"], 1):
            where = f"ch{ci:02d}.p{pi:02d}"
            text = join(p["lines"])
            for line in p["lines"]:
                if MD_LEAK_RE.search(line):
                    fails.append(f"{where} Markdown 符號會被念出：{line[:20]}")
            if len(text) > max_para:
                warns.append(f"{where} 段長 {len(text)} > {max_para}（拆段）")
            if text.rstrip(CLOSERS)[-1:] not in FINAL_PUNCT:
                warns.append(f"{where} 段末無句末標點：…{text[-8:]}")
            for sent in split_sentences(text):
                if len(sent) > seg_max:
                    fails.append(f"{where} 單句 {len(sent)} 字 > {seg_max}：{sent[:16]}…")
                elif len(sent) > args.max_sentence:
                    warns.append(f"{where} 單句 {len(sent)} 字 > {args.max_sentence}：{sent[:16]}…")
            for name, rx, hint in LINT_RULES:
                hit = rx.search(text)
                if hit:
                    warns.append(f"{where} {name}「{hit.group(0)[:10]}」：{hint}")

    for label, items in (("FAIL", fails), ("WARN", warns)):
        for item in items[:40]:
            print(f"{label} {item}")
        if len(items) > 40:
            print(f"{label} ... 另 {len(items) - 40} 則")
    print(f"\nresult: {len(fails)} FAIL, {len(warns)} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
