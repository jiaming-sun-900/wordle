"""Build dict.json for Word Duo's answer card from ECDICT (MIT, github.com/skywind3000/ECDICT).

Usage: python3 -I tools/build-dict.py <ecdict.csv> <answers.json> [extra words...] > dict.json

Only the words the game can pick as an answer are kept, so the output stays small.
Each entry is [phonetic, chinese]:
  phonetic  ECDICT's transcription, normalised to IPA stress/schwa marks
  chinese   part-of-speech lines such as "v. 喷鼻息；嗤之以鼻", newline-separated
English definitions are left to dictionaryapi.dev at runtime: ECDICT's come from WordNet, whose
sense order is not by frequency (its first "crane" is the American writer).
"""
import csv
import json
import re
import sys

MAX_ZH_LINES = 3      # one per part of speech is plenty on a card
MAX_ZH_SENSES = 4     # meanings kept per line
SENSE_SPLIT = re.compile(r"[；;，,](?![^()（）]*[)）])")  # separators outside parentheses


def zh_lines(raw):
    lines = [l.strip() for l in raw.replace("\\n", "\n").split("\n") if l.strip()]
    # "[网络]" lines are crowd-sourced web glosses; use them only when nothing else exists.
    proper = [l for l in lines if not l.startswith("[")]
    lines = proper or [re.sub(r"^\[[^\]]*\]\s*", "", l) for l in lines]
    out = []
    for line in lines[:MAX_ZH_LINES]:
        m = re.match(r"^((?:[a-z]+\.\s*)+)?(.*)$", line)
        pos, body = (m.group(1) or "").strip(), m.group(2)
        senses = [s.strip() for s in SENSE_SPLIT.split(body) if s.strip()]
        out.append((pos + " " if pos else "") + "；".join(senses[:MAX_ZH_SENSES]))
    return "\n".join(out)


def ipa(raw):
    first = raw.strip().split(", ")[0]  # "reif, rælf" lists alternatives; keep the first
    return first.replace("'", "ˈ").replace(",", "ˌ").replace("ә", "ə")


def main():
    csv_path, answers_path, *extra = sys.argv[1:]
    with open(answers_path, encoding="utf-8") as f:
        wanted = {w for w in json.load(f) if isinstance(w, str) and re.fullmatch(r"[a-z]{5}", w)}
    wanted.update(w for w in extra if re.fullmatch(r"[a-z]{5}", w))

    found = {}
    csv.field_size_limit(10_000_000)
    with open(csv_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            raw = (row.get("word") or "").strip()
            w = raw.lower()
            if w not in wanted:
                continue
            zh = zh_lines(row.get("translation") or "")
            if not zh:
                continue
            # A lowercase headword beats a capitalised one (china the porcelain over China the country).
            if w in found and not (raw == w and found[w][2] != w):
                continue
            found[w] = [ipa(row.get("phonetic") or ""), zh, raw]

    missing = sorted(wanted - found.keys())
    print(f"{len(found)}/{len(wanted)} words; missing: {' '.join(missing) or 'none'}", file=sys.stderr)
    out = {w: e[:2] for w, e in sorted(found.items())}
    json.dump(out, sys.stdout, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
