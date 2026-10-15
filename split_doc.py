#!/usr/bin/env python3
"""
Rozdziela pliki .md na business_logic/ i architecture/.

Struktura:
  src/*.md            11 plików wejściowych (sortowane alfabetycznie -> F01..F11)
  work/NN.units.json  pełna segmentacja (generuje `segment`)
  work/NN.to_tag.json wejście dla Claude (generuje `segment`)
  work/NN.tags.json   klasyfikacja jednostek (generuje agent)
  business_logic/ wynik biznesowy (generuje `assemble`)
  architecture/       wynik (generuje `assemble`)

Użycie:
  python split_doc.py segment
  python split_doc.py assemble
  python split_doc.py check
"""
import json
import re
import sys
from pathlib import Path

SRC, WORK = Path("src"), Path("work")
BL_DIR, AR_DIR = Path("business_logic"), Path("architecture")

TECH = re.compile(
    r"\b(REST|GraphQL|endpoint\w*|HTTPS?|JSON|SQL|Kafka|Redis|API|gRPC|"
    r"microservice\w*|Docker|Kubernetes|POST|GET|PUT|DELETE|queue|schema|cache\w*)\b",
    re.I,
)
HEADING = re.compile(r"#{1,6} ")


def split_units(text):
    """Dzieli markdown na bloki: nagłówek = osobna jednostka, bloki kodu nienaruszone."""
    units, buf, fence = [], [], False

    def flush():
        if buf:
            units.append("\n".join(buf).strip("\n"))
            buf.clear()

    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and not line.strip():
            flush()
            continue
        if not fence and HEADING.match(line):
            flush()
            units.append(line)
            continue
        buf.append(line)
    flush()
    return [u for u in units if u.strip()]


def sources():
    files = sorted(SRC.glob("*.md"))
    if not files:
        sys.exit("Brak plików w src/*.md")
    return list(enumerate(files, 1))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def segment():
    WORK.mkdir(exist_ok=True)
    for i, f in sources():
        units, path = [], []
        for n, text in enumerate(split_units(f.read_text(encoding="utf-8")), 1):
            uid = f"F{i:02d}-U{n:03d}"
            if HEADING.match(text):
                level = len(text) - len(text.lstrip("#"))
                path = path[: level - 1] + [text.lstrip("# ").strip()]
                units.append({"id": uid, "kind": "heading", "text": text})
            else:
                units.append(
                    {"id": uid, "kind": "block", "heading_path": " > ".join(path), "text": text}
                )
        (WORK / f"{i:02d}.units.json").write_text(
            json.dumps(units, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        to_tag = [
            {"id": u["id"], "heading_path": u["heading_path"], "text": u["text"]}
            for u in units
            if u["kind"] == "block"
        ]
        (WORK / f"{i:02d}.to_tag.json").write_text(
            json.dumps(to_tag, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"{f.name}: {len(to_tag)} jednostek do tagowania")


def assemble():
    BL_DIR.mkdir(exist_ok=True)
    AR_DIR.mkdir(exist_ok=True)
    for i, f in sources():
        units = load(WORK / f"{i:02d}.units.json")
        tags_path = WORK / f"{i:02d}.tags.json"
        if not tags_path.exists():
            print(f"POMIJAM {f.name}: brak {tags_path}")
            continue
        tags = {t["id"]: t for t in load(tags_path)}
        bl, ar = [], []
        for u in units:
            uid, text = u["id"], u["text"]
            if u["kind"] == "heading":
                bl.append(text)
                ar.append(text)
                continue
            t = tags.get(uid)
            if t is None:
                msg = f"<!-- {uid} UNTAGGED -->\n{text}"
                bl.append(msg)
                ar.append(msg)
            elif t["tag"] == "BL":
                bl.append(f"<!-- {uid} -->\n{text}")
            elif t["tag"] == "ARCH":
                ar.append(f"<!-- {uid} -->\n{text}")
            else:  # MIXED
                if t.get("bl_text"):
                    bl.append(f"<!-- {uid} | see: architecture/{f.name} -->\n{t['bl_text']}")
                if t.get("arch_text"):
                    ar.append(f"<!-- {uid} | see: business_logic/{f.name} -->\n{t['arch_text']}")
        head = f"<!-- source: src/{f.name} -->\n\n"
        (BL_DIR / f.name).write_text(head + "\n\n".join(bl) + "\n", encoding="utf-8")
        (AR_DIR / f.name).write_text(head + "\n\n".join(ar) + "\n", encoding="utf-8")
        print(f"OK {f.name}")


def check():
    problems = 0
    low_conf = []
    for i, f in sources():
        units = load(WORK / f"{i:02d}.units.json")
        tags_path = WORK / f"{i:02d}.tags.json"
        if not tags_path.exists():
            print(f"[{f.name}] brak tags.json")
            problems += 1
            continue
        tags = {t["id"]: t for t in load(tags_path)}
        bl_text = (BL_DIR / f.name).read_text(encoding="utf-8") if (BL_DIR / f.name).exists() else ""
        ar_text = (AR_DIR / f.name).read_text(encoding="utf-8") if (AR_DIR / f.name).exists() else ""

        for u in units:
            if u["kind"] != "block":
                continue
            uid = u["id"]
            if uid not in tags:
                print(f"[{f.name}] BRAK TAGU: {uid}")
                problems += 1
            elif tags[uid].get("confidence", 1) < 0.7:
                low_conf.append(uid)
            if f"<!-- {uid} " not in bl_text and f"<!-- {uid} " not in ar_text:
                print(f"[{f.name}] NIEOBECNE W WYNIKU: {uid}")
                problems += 1

        extra = set(tags) - {u["id"] for u in units}
        for uid in sorted(extra):
            print(f"[{f.name}] NADMIAROWY TAG: {uid}")
            problems += 1

        # czystość: technologie w BL (poza komentarzami)
        for line in re.sub(r"<!--.*?-->", "", bl_text, flags=re.DOTALL).splitlines():
            m = TECH.search(line)
            if m:
                print(f"[BL {f.name}] technologia '{m.group(0)}': {line.strip()[:80]}")
                problems += 1

    if low_conf:
        print(f"\nNiska pewność (<0.7), do ręcznego przeglądu: {', '.join(low_conf)}")
    print(f"\nProblemów: {problems}")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    cmds = {"segment": segment, "assemble": assemble, "check": check}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]]()
