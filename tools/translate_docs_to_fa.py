import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Iterable, List

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CODE_FENCE_PATTERN = re.compile(r"(```.*?```|~~~.*?~~~)", re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r"`[^`]+`")
PLACEHOLDER_CODE = "[[CODE_BLOCK_{idx}]]"
PLACEHOLDER_INLINE = "[[INLINE_{idx}]]"
MAX_CHARS = 700


class GoogleAPISession:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self.url = "https://translate.googleapis.com/translate_a/single"

    def translate(self, text: str, target: str = "fa", source: str = "auto") -> str:
        params = {
            "client": "gtx",
            "sl": source,
            "tl": target,
            "dt": "t",
            "q": text,
        }
        resp = self.session.get(self.url, params=params, timeout=60, verify=False)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            snippet = resp.text[:200]
            raise RuntimeError(f"Translation HTTP error {resp.status_code}: {snippet}") from exc
        try:
            data = resp.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Failed to decode translation response: {resp.text[:200]}") from exc
        return "".join(part[0] for part in data[0] if part and part[0])


def mask_code_blocks(text: str):
    code_blocks: List[str] = []

    def repl(match):
        code_blocks.append(match.group(0))
        return PLACEHOLDER_CODE.format(idx=len(code_blocks) - 1)

    return CODE_FENCE_PATTERN.sub(lambda m: repl(m), text), code_blocks


def mask_inline_code(text: str):
    inline_blocks: List[str] = []

    def repl(match):
        inline_blocks.append(match.group(0))
        return PLACEHOLDER_INLINE.format(idx=len(inline_blocks) - 1)

    return INLINE_CODE_PATTERN.sub(lambda m: repl(m), text), inline_blocks


def restore_placeholders(text: str, placeholders: Iterable[str], template: str):
    for idx, value in enumerate(placeholders):
        text = text.replace(template.format(idx=idx), value)
    return text


def chunk_text(text: str, max_chars: int = MAX_CHARS) -> List[str]:
    chunks: List[str] = []
    current = []
    current_len = 0
    for line in text.splitlines(keepends=True):
        if current_len + len(line) > max_chars and current:
            chunks.append("".join(current))
            current = [line]
            current_len = len(line)
        else:
            current.append(line)
            current_len += len(line)
    if current:
        chunks.append("".join(current))
    return chunks if chunks else [text]


def translate_markdown(content: str, translator: GoogleAPISession) -> str:
    masked_code, code_blocks = mask_code_blocks(content)
    masked_inline, inline_blocks = mask_inline_code(masked_code)

    translated_segments = []
    for chunk in chunk_text(masked_inline):
        translated_segments.append(translator.translate(chunk))
    translated = "".join(translated_segments)

    translated = restore_placeholders(translated, inline_blocks, PLACEHOLDER_INLINE)
    translated = restore_placeholders(translated, code_blocks, PLACEHOLDER_CODE)
    return translated


def process_file(path: Path, base_dir: Path, translator: GoogleAPISession, output_root: Path | None = None) -> Path:
    rel_path = path.relative_to(base_dir)
    output_dir = (output_root or base_dir) / rel_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"FA_{path.name}"

    content = path.read_text(encoding="utf-8")
    translated_body = translate_markdown(content, translator)

    header = "\n".join([
        "<!-- ",
        f"  Translated into Persian (Farsi) from {path.name}",
        f"  Date: {date.today().isoformat()}",
        "-->",
        "",
    ])
    output_path.write_text(header + translated_body, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Translate Markdown files to Persian with FA_ prefix.")
    parser.add_argument("base_dir", nargs="?", default="docs", help="Directory to scan for Markdown files")
    parser.add_argument("--output-root", default=None, help="Optional output root; defaults to same tree")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    if not base_dir.exists():
        raise SystemExit(f"Base directory {base_dir} does not exist")

    output_root = Path(args.output_root).resolve() if args.output_root else None
    translator = GoogleAPISession()

    md_files: list[Path] = [
        path for path in sorted(base_dir.rglob("*.md")) if not path.name.startswith("FA_")
    ]
    if not md_files:
        print(f"No markdown files found under {base_dir}")
        return

    generated = []
    for md_path in md_files:
        print(f"Translating {md_path}")
        generated.append(process_file(md_path, base_dir, translator, output_root))

    print("Processed files:")
    for src, out in zip(md_files, generated):
        print(f"- {src} -> {out}")


if __name__ == "__main__":
    main()
