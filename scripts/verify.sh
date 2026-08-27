#!/bin/sh
set -eu

PROJECT_ROOT=${VERIFY_ROOT:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}
CXX_BIN=${CXX:-clang++}

command -v "$CXX_BIN" >/dev/null 2>&1 || {
    echo "Nie znaleziono kompilatora: $CXX_BIN" >&2
    exit 1
}

echo "Sprawdzanie Markdown i przykładów przez $($CXX_BIN --version | sed -n '1p')"

python3 - "$PROJECT_ROOT" "$CXX_BIN" <<'PY'
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
compiler = sys.argv[2]
files = sorted(
    path for path in root.rglob("*.md")
    if ".git" not in path.parts and "docs/superpowers" not in path.as_posix()
)
errors: list[str] = []
blocks: list[tuple[Path, int, str]] = []
link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
fence_re = re.compile(r"^\s*(```|~~~)(.*)$")
depth_sections = (
    "Jak to działa krok po kroku",
    "Pogłębienie mechanizmu",
    "Drugi przykład",
    "Porównanie i decyzje",
)

for path in files:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(root)
    if not text.strip():
        errors.append(f"Pusty plik: {rel}")
        continue

    lines = text.splitlines()
    in_fence = False
    marker = ""
    info = ""
    start = 0
    code: list[str] = []
    prose: list[str] = []
    example_blocks = 0

    for number, line in enumerate(lines, 1):
        match = fence_re.match(line)
        if match:
            token, rest = match.group(1), match.group(2).strip()
            if not in_fence:
                in_fence = True
                marker = token
                info = rest
                start = number
                code = []
            elif token == marker:
                example_blocks += 1
                if info == "cpp":
                    blocks.append((rel, start, "\n".join(code) + "\n"))
                in_fence = False
                marker = info = ""
                code = []
            else:
                code.append(line)
            continue

        if in_fence:
            code.append(line)
            continue

        prose.append(line)

        for target in link_re.findall(line):
            clean = target.strip().strip("<>").split("#", 1)[0]
            if not clean or clean.startswith(("http://", "https://", "mailto:")):
                continue
            destination = (path.parent / clean).resolve()
            try:
                destination.relative_to(root.resolve())
            except ValueError:
                errors.append(f"Link poza projektem: {rel}:{number} -> {target}")
                continue
            if not destination.exists():
                errors.append(f"Martwy link: {rel}:{number} -> {target}")

    if in_fence:
        errors.append(f"Niedomknięty blok kodu: {rel}:{start}")

    is_chapter = (
        len(rel.parts) == 2
        and (re.fullmatch(r"\d{2}_.+", rel.parts[0]) or rel.parts[0] == "zaawansowane")
        and rel.name != "README.md"
    )
    if is_chapter:
        min_words = 650 if rel.parts[0] == "zaawansowane" else 500
        prose_words = re.findall(r"[^\W_]+(?:[’'-][^\W_]+)*|\d+", "\n".join(prose), re.UNICODE)
        if len(prose_words) < min_words:
            errors.append(
                f"Za mało słów prozy: {rel} — {len(prose_words)}, wymagane minimum {min_words}"
            )
        for section in depth_sections:
            if f"## {section}" not in text:
                errors.append(f"Brak sekcji pogłębienia: {rel} -> ## {section}")
        if example_blocks < 2:
            errors.append(
                f"Za mało bloków przykładów: {rel} — {example_blocks}, wymagane minimum 2"
            )
        if not lines or lines[0].strip() != "[← Spis treści](../README.md)":
            errors.append(f"Brak linku powrotnego na początku: {rel}")
        if "## Powiązane tematy" not in text:
            errors.append(f"Brak sekcji Powiązane tematy: {rel}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)

compiled = 0
with tempfile.TemporaryDirectory(prefix="kompendium-cpp-") as temp:
    temp_dir = Path(temp)
    for index, (source, line, code) in enumerate(blocks, 1):
        unit = temp_dir / f"example_{index}.cpp"
        unit.write_text(code, encoding="utf-8")
        result = subprocess.run(
            [compiler, "-std=c++23", "-Wall", "-Wextra", "-Wpedantic", "-fsyntax-only", str(unit)],
            text=True,
            capture_output=True,
        )
        if result.returncode:
            print(f"Błąd przykładu {source}:{line}", file=sys.stderr)
            print(result.stdout, end="", file=sys.stderr)
            print(result.stderr, end="", file=sys.stderr)
            raise SystemExit(result.returncode)
        compiled += 1

print(f"Markdown: {len(files)} plików; przykłady C++23: {compiled}; wynik: OK")
PY
