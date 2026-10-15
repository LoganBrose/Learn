#!/usr/bin/env python3
"""Check that every lesson file is well-formed and matches the manifest.

Usage:  python3 tools/validate.py      (run from the daily-learn folder or anywhere)
Only uses the Python standard library.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS = ROOT / "lessons"
CATS = {"science", "history", "engineering", "economics", "psychology",
        "geography", "math", "technology", "nature", "random"}

errors = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def extract_calls(text, func):
    """Return the JSON argument of every `func(` call in a JS file."""
    dec = json.JSONDecoder()
    out = []
    for m in re.finditer(r"^" + re.escape(func) + r"\(", text, re.MULTILINE):
        value, _ = dec.raw_decode(text, m.end())
        out.append(value)
    return out


def text_ok(where, value, min_len=1):
    if not isinstance(value, str) or len(value.strip()) < min_len:
        err(where, f"expected text (at least {min_len} chars)")


def check_lesson(L, chunk_no):
    w = L.get("id", "<no id>")
    for key in ("id", "title", "category", "hook", "sections", "teachBack", "quiz", "goDeeper"):
        if key not in L:
            err(w, f"missing '{key}'")
    if L.get("category") not in CATS:
        err(w, f"bad category {L.get('category')!r}")
    text_ok(w + ".hook", L.get("hook", ""), 80)
    secs = L.get("sections", [])
    if not 4 <= len(secs) <= 6:
        err(w, f"needs 4-6 sections, has {len(secs)}")
    for i, s in enumerate(secs):
        text_ok(f"{w}.sections[{i}].heading", s.get("heading"))
        text_ok(f"{w}.sections[{i}].body", s.get("body"), 120)
    d = L.get("diagram")
    if d is not None:
        try:
            ET.fromstring(d["svg"])
        except Exception as e:  # noqa: BLE001
            err(w, f"diagram SVG does not parse: {e}")
        if not 0 <= d.get("after", 1) < len(secs):
            err(w, "diagram 'after' index out of range")
    tb = L.get("teachBack", [])
    if len(tb) != 3:
        err(w, f"needs 3 teach-back questions, has {len(tb)}")
    for i, t in enumerate(tb):
        text_ok(f"{w}.teachBack[{i}].q", t.get("q"))
        text_ok(f"{w}.teachBack[{i}].model", t.get("model"), 40)
    qz = L.get("quiz", [])
    if len(qz) != 5:
        err(w, f"needs 5 quiz questions, has {len(qz)}")
    for i, q in enumerate(qz):
        opts, exp = q.get("options", []), q.get("explain", [])
        if len(opts) != 4 or len(exp) != 4:
            err(f"{w}.quiz[{i}]", "needs 4 options and 4 explanations")
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] < len(opts):
            err(f"{w}.quiz[{i}]", "answer index out of range")
        text_ok(f"{w}.quiz[{i}].q", q.get("q"))
    gd = L.get("goDeeper", [])
    if not 2 <= len(gd) <= 3:
        err(w, f"needs 2-3 go-deeper items, has {len(gd)}")


def main():
    manifest = extract_calls((LESSONS / "manifest.js").read_text(encoding="utf-8"), "DL.setManifest")[0]
    ids = [t["id"] for t in manifest]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        err("manifest", f"duplicate ids {sorted(dupes)}")

    lessons = {}
    for f in sorted(LESSONS.glob("lessons-*.js")):
        chunk_no = int(f.stem.split("-")[1])
        for batch in extract_calls(f.read_text(encoding="utf-8"), "DL.add"):
            for L in batch:
                if L.get("id") in lessons:
                    err(f.name, f"duplicate lesson id {L.get('id')}")
                lessons[L.get("id")] = (L, chunk_no)
                check_lesson(L, chunk_no)

    for t in manifest:
        if t["id"] not in lessons:
            err("manifest", f"{t['id']} has no lesson in any lessons file")
            continue
        L, chunk_no = lessons[t["id"]]
        if t["chunk"] != chunk_no:
            err("manifest", f"{t['id']} says chunk {t['chunk']} but is in lessons-{chunk_no:02d}.js")
        if t["title"] != L["title"] or t["category"] != L["category"]:
            err("manifest", f"{t['id']} title/category differ from the lesson file")
    for lid in lessons:
        if lid not in ids:
            err("manifest", f"lesson {lid} is not listed in manifest.js")

    by_cat = {}
    for t in manifest:
        by_cat[t["category"]] = by_cat.get(t["category"], 0) + 1
    print(f"{len(manifest)} topics in manifest, {len(lessons)} lessons written")
    print("per category:", ", ".join(f"{c} {by_cat.get(c, 0)}" for c in sorted(CATS)))
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("All good.")


if __name__ == "__main__":
    main()
