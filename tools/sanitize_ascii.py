#!/usr/bin/env python3
import sys, re, pathlib

ASCII_OK = re.compile(rb'^[\x09\x0a\x0d\x20-\x7e]*$')
REPLACEMENTS = {
    "\u201c": '"', "\u201d": '"',
    "\u2018": "'", "\u2019": "'",
    "\u2013": "-", "\u2014": "-",
    "\u2026": "...",
    "\u00A0": " ",
    "\u200C": "",  "\u200D": "",
}
BI_DI = re.compile(r'[\u200E\u200F\u202A-\u202E]')
CODE_EXTS = {
    ".ps1",".psd1",".psm1",".sh",".bash",".zsh",".bat",".cmd",
    ".js",".mjs",".cjs",".ts",".tsx",".jsx",".json",
    ".py",".go",".rs",".java",".cs",".cpp",".c",".h",
    ".yaml",".yml",".toml",".ini",".env",".sql",".tf",".dockerfile"
}
SKIP_DIRS = {".git",".github",".venv","venv","node_modules","dist","build","out",".next","__pycache__"}

def normalize_text(txt:str)->str:
    for k,v in REPLACEMENTS.items():
        txt = txt.replace(k, v)
    txt = BI_DI.sub("", txt)
    return txt

def is_code_file(p: pathlib.Path)->bool:
    if p.suffix.lower() in CODE_EXTS: return True
    return p.name.lower() in {"dockerfile","makefile",".env",".env.example","justfile"}

def main():
    repo = pathlib.Path(".").resolve()
    changed, failed = [], []
    for p in repo.rglob("*"):
        if not p.is_file(): continue
        if any(part in SKIP_DIRS for part in p.parts): continue
        if not is_code_file(p): continue
        raw = p.read_bytes()
        if ASCII_OK.match(raw): continue
        try: s = raw.decode("utf-8", errors="replace")
        except: s = raw.decode("latin-1", errors="replace")
        s2 = normalize_text(s)
        b2 = s2.encode("utf-8")
        b3 = bytearray()
        for ch in b2:
            if ch in (9,10,13) or 32 <= ch <= 126: b3.append(ch)
        if bytes(b3) != raw:
            p.write_bytes(bytes(b3))
            changed.append(str(p))
        if not ASCII_OK.match(bytes(b3)):
            failed.append(str(p))
    if changed:
        print("[sanitize] fixed files:"); [print("  -", f) for f in changed]
    if failed:
        print("\n[ERROR] still non-ASCII files:"); [print("  -", f) for f in failed]
        sys.exit(2)
    print("\nOK: all code files are ASCII-only."); return 0

if __name__ == "__main__":
    sys.exit(main())
