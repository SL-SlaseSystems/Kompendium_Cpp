#!/usr/bin/env python3
"""Validate the compendium's Markdown, navigation and standalone C++23 examples.

API: ``validate(root, section=None, metadata_only=False, compiler=None,
compile_timeout=30)`` returns a ``ValidationResult`` with ``errors`` and numeric
``metrics``. ``parse_markdown(text)`` exposes fence-aware prose, links and blocks
for small tests/tools. Only NN_*.md directly inside NN_* or zaawansowane are
chapters; worksheets, maps, cwiczenia and praktyka do not use chapter templates.

CLI defaults to all metadata checks plus syntax-only compilation of each closed
``cpp`` fence. ``cpp,notest`` is excluded. No example is executed. Compilation
starts only after metadata passes. --metadata-only needs no compiler; --section
checks only one immediate section directory and skips global index completeness.
The selected section's links are still checked against the full repository root.

--metrics writes exactly one JSON object to stdout (also on failure):
markdown_files counts discovered .md files, including unreadable/empty ones;
main_chapters/expert_chapters count the chapter filenames described above;
section_maps counts README.md inside numbered sections or zaawansowane;
exercise_sets counts ZESTAW-CWICZEN.md in those sections; cpp_blocks counts
closed testable cpp fences, even when --metadata-only skips their compilation;
compiled_blocks counts successful compiler calls; errors is a list of diagnostics.
Every count uses the current --section scope and excludes ignored directories.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlsplit

SECTION_RE = re.compile(r'\d{2}_.+')
CHAPTER_RE = re.compile(r'\d{2}_.+\.md')
FENCE_RE = re.compile(r'^[ \t]*(`{3,}|~{3,})(.*)$')
HEADING_RE = re.compile(r'^ {0,3}##[ \t]+(.+?)[ \t]*#*[ \t]*$')
DEPTH_SECTIONS = (
    'Jak to działa krok po kroku',
    'Pogłębienie mechanizmu',
    'Drugi przykład',
    'Porównanie i decyzje',
)
IGNORED_DIRS = {'.git', '__pycache__', 'build'}


@dataclass(frozen=True)
class Link:
    line: int
    target: str


@dataclass(frozen=True)
class CodeBlock:
    line: int
    info: str
    code: str

    @property
    def testable_cpp(self) -> bool:
        tokens = self.info.replace(',', ' ').split()
        return bool(tokens) and tokens[0] == 'cpp' and 'notest' not in tokens[1:]


@dataclass
class ParsedMarkdown:
    prose: list[tuple[int, str]] = field(default_factory=list)
    blocks: list[CodeBlock] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
    unclosed_fence: int | None = None


@dataclass
class ValidationResult:
    metrics: dict[str, int]
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, object]:
        return {**self.metrics, 'errors': self.errors}


def _destination(raw: str) -> str:
    """Extract a Markdown destination, leaving optional link titles behind."""
    raw = raw.strip()
    if raw.startswith('<'):
        end = raw.find('>')
        return raw[1:end] if end >= 0 else raw[1:]
    match = re.match(r'(?:\\.|[^\s])+', raw)
    return re.sub(r'\\([!"#$%&\'()*+,\-./:;<=>?@\[\]\\^_`{|}~])', r'\1', match.group(0)) if match else ''


def _line_links(line: str, number: int) -> Iterable[Link]:
    if line.startswith(('    ', '\t')):
        return
    # Backtick spans are code too. Preserve the prose on either side of them.
    prose = re.sub(r'(?<!`)(`+)(?!`)(.*?)\1(?!`)', '', line)
    definition = re.match(r'^ {0,3}\[[^\]]+\]:\s*(.+)$', prose)
    if definition:
        yield Link(number, _destination(definition.group(1)))
        return
    for match in re.finditer(r'!?\[(?:\\.|[^\]\\])*\]\(', prose):
        cursor = match.end()
        start = cursor
        depth = 1
        in_angle = False
        while cursor < len(prose):
            char = prose[cursor]
            if char == '\\':
                cursor += 2
                continue
            if char == '<':
                in_angle = True
            elif char == '>':
                in_angle = False
            elif not in_angle:
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        yield Link(number, _destination(prose[start:cursor]))
                        break
            cursor += 1


def parse_markdown(text: str) -> ParsedMarkdown:
    """Separate prose from fenced code without interpreting links inside code."""
    parsed = ParsedMarkdown()
    marker = ''
    info = ''
    start = 0
    code: list[str] = []
    for number, line in enumerate(text.splitlines(), 1):
        fence = FENCE_RE.match(line)
        if marker:
            if (fence and fence.group(1)[0] == marker[0]
                    and len(fence.group(1)) >= len(marker) and not fence.group(2).strip()):
                parsed.blocks.append(CodeBlock(start, info, '\n'.join(code) + '\n'))
                marker = ''
                code = []
            else:
                code.append(line)
        elif fence:
            marker, info = fence.group(1), fence.group(2).strip()
            start = number
        else:
            parsed.prose.append((number, line))
            parsed.links.extend(_line_links(line, number))
    if marker:
        parsed.unclosed_fence = start
    return parsed


def _is_section(name: str) -> bool:
    return bool(SECTION_RE.fullmatch(name)) or name == 'zaawansowane'


def _is_chapter(relative: Path) -> bool:
    return len(relative.parts) == 2 and _is_section(relative.parts[0]) and bool(CHAPTER_RE.fullmatch(relative.name))


def _markdown_files(root: Path, start: Path) -> list[Path]:
    files: list[Path] = []
    for directory, dirs, names in os.walk(start, followlinks=False):
        current = Path(directory)
        dirs[:] = sorted(name for name in dirs
                         if name not in IGNORED_DIRS
                         and not name.startswith('cmake-build-')
                         and (current / name).relative_to(root).as_posix() != 'docs/superpowers'
                         and not (current / name).is_symlink())
        files.extend(current / name for name in sorted(names) if name.endswith('.md'))
    return sorted(files)


def _local_destination(root: Path, source: Path, link: Link, errors: list[str]) -> Path | None:
    try:
        url = urlsplit(link.target)
        if url.scheme.lower() in ('http', 'https', 'mailto') or link.target.startswith('//'):
            return None
        if not url.path:
            return None
        destination = (source.parent / unquote(url.path)).resolve()
        destination.relative_to(root)
    except (ValueError, OSError, RuntimeError):
        errors.append(f'Link poza projektem: {source.relative_to(root)}:{link.line} -> {link.target}')
        return None
    if not destination.exists():
        errors.append(f'Martwy link: {source.relative_to(root)}:{link.line} -> {link.target}')
    return destination


def _validate_chapter(relative: Path, parsed: ParsedMarkdown, errors: list[str]) -> None:
    minimum = 650 if relative.parts[0] == 'zaawansowane' else 500
    prose = '\n'.join(line for _, line in parsed.prose)
    words = re.findall(r'[^\W_]+(?:[’\'-][^\W_]+)*|\d+', prose, re.UNICODE)
    if len(words) < minimum:
        errors.append(f'Za mało słów prozy: {relative} — {len(words)}, wymagane minimum {minimum}')
    headings = [match.group(1).strip() for _, line in parsed.prose if (match := HEADING_RE.match(line))]
    for section in DEPTH_SECTIONS:
        if section not in headings:
            errors.append(f'Brak sekcji pogłębienia: {relative} -> ## {section}')
    if len(parsed.blocks) < 2:
        errors.append(f'Za mało bloków przykładów: {relative} — {len(parsed.blocks)}, wymagane minimum 2')
    navigation = False
    for link in parsed.links:
        if link.line != 1:
            continue
        try:
            target = urlsplit(link.target)
        except ValueError:
            continue
        if not target.scheme and not target.netloc and unquote(target.path) in ('../README.md', 'README.md', './README.md'):
            navigation = True
    if not navigation:
        errors.append(f'Brak linku powrotnego na początku: {relative}')
    if not headings or headings[-1] != 'Powiązane tematy':
        errors.append(f'Brak końcowej sekcji Powiązane tematy: {relative}')


def _validate_indexes(root: Path, files: list[Path], sections: list[Path], links: dict[Path, set[Path]],
                      errors: list[str], *, scoped: bool) -> None:
    chapters = [path for path in files if _is_chapter(path.relative_to(root))]
    if not scoped:
        index = root / 'README.md'
        if not index.is_file():
            errors.append('Brak głównego indeksu: README.md')
        index_links = links.get(index, set())
        for chapter in chapters:
            if chapter not in index_links:
                errors.append(f'Brak rozdziału w głównym indeksie: {chapter.relative_to(root)}')
        for section in sections:
            if section / 'README.md' not in index_links:
                errors.append(f'Brak mapy w głównym indeksie: {section.name}/README.md')
    for section in sections:
        section_map = section / 'README.md'
        if not section_map.is_file():
            errors.append(f'Brak mapy działu: {section.name}/README.md')
        map_links = links.get(section_map, set())
        for chapter in chapters:
            if chapter.parent == section and chapter not in map_links:
                errors.append(f'Brak rozdziału w mapie: {section.name}/README.md -> {chapter.name}')
        # Exercise sets are mandatory for the numbered curriculum 01–30.
        if SECTION_RE.fullmatch(section.name) and 1 <= int(section.name[:2]) <= 30:
            worksheet = section / 'ZESTAW-CWICZEN.md'
            if not worksheet.is_file():
                errors.append(f'Brak zestawu ćwiczeń: {section.name}/ZESTAW-CWICZEN.md')
            if worksheet not in map_links:
                errors.append(f'Brak zestawu ćwiczeń w mapie: {section.name}/README.md')


def _compile_blocks(blocks: list[tuple[Path, CodeBlock]], compiler: str,
                    result: ValidationResult, timeout: float) -> None:
    if not blocks:
        return
    executable = shutil.which(compiler)
    if executable is None:
        result.errors.append(f'Nie znaleziono kompilatora: {compiler}')
        return
    with tempfile.TemporaryDirectory(prefix='kompendium-cpp-') as temp:
        for index, (source, block) in enumerate(blocks, 1):
            unit = Path(temp) / f'example_{index}.cpp'
            unit.write_text(block.code, encoding='utf-8')
            command = [executable, '-std=c++23', '-pthread', '-Wall', '-Wextra', '-Wpedantic', '-fsyntax-only', str(unit)]
            try:
                completed = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
            except subprocess.TimeoutExpired:
                result.errors.append(f'Przekroczono czas kompilacji ({timeout:g} s): {source}:{block.line}')
                continue
            except OSError as exc:
                result.errors.append(f'Nie można uruchomić kompilatora {compiler}: {exc}')
                break
            if completed.returncode:
                diagnostic = (completed.stdout + completed.stderr).strip()
                result.errors.append(f'Błąd przykładu {source}:{block.line}\n{diagnostic}')
            else:
                result.metrics['compiled_blocks'] += 1


def validate(root: Path | str, *, section: str | None = None, metadata_only: bool = False,
             compiler: str | None = None, compile_timeout: float = 30) -> ValidationResult:
    """Validate a repository or a section; return diagnostics without printing/exiting."""
    result = ValidationResult({key: 0 for key in ('markdown_files', 'main_chapters', 'expert_chapters',
                                                'cpp_blocks', 'section_maps', 'exercise_sets', 'compiled_blocks')})
    root = Path(root).resolve()
    if not root.is_dir():
        result.errors.append(f'Nie znaleziono katalogu projektu: {root}')
        return result
    if section is not None:
        start = root / section
        if (Path(section).name != section or not _is_section(section) and section not in ('cwiczenia', 'praktyka')
                or not start.is_dir() or start.is_symlink()):
            result.errors.append(f'Nieznany dział: {section}')
            return result
    else:
        start = root
    files = _markdown_files(root, start)
    sections = sorted(path for path in root.iterdir()
                      if path.is_dir() and not path.is_symlink() and _is_section(path.name)
                      and (section is None or path.name == section))
    result.metrics['markdown_files'] = len(files)
    links: dict[Path, set[Path]] = {}
    blocks: list[tuple[Path, CodeBlock]] = []
    for path in files:
        relative = path.relative_to(root)
        if _is_chapter(relative):
            result.metrics['expert_chapters' if relative.parts[0] == 'zaawansowane' else 'main_chapters'] += 1
        if len(relative.parts) == 2 and _is_section(relative.parts[0]):
            if relative.name == 'README.md':
                result.metrics['section_maps'] += 1
            elif relative.name == 'ZESTAW-CWICZEN.md':
                result.metrics['exercise_sets'] += 1
        try:
            # A Markdown symlink may not make us read outside the repository either.
            path.resolve().relative_to(root)
            text = path.read_text(encoding='utf-8')
        except UnicodeError as exc:
            result.errors.append(f'Niepoprawny UTF-8: {relative}: {exc}')
            continue
        except (OSError, ValueError, RuntimeError) as exc:
            result.errors.append(f'Nie można odczytać Markdown: {relative}: {exc}')
            continue
        if not text.strip():
            result.errors.append(f'Pusty plik: {relative}')
        parsed = parse_markdown(text)
        if parsed.unclosed_fence is not None:
            result.errors.append(f'Niedomknięty blok kodu: {relative}:{parsed.unclosed_fence}')
        destinations = set()
        for link in parsed.links:
            destination = _local_destination(root, path, link, result.errors)
            if destination is not None:
                destinations.add(destination)
        links[path] = destinations
        blocks.extend((relative, block) for block in parsed.blocks if block.testable_cpp)
        if _is_chapter(relative):
            _validate_chapter(relative, parsed, result.errors)
    result.metrics['cpp_blocks'] = len(blocks)
    _validate_indexes(root, files, sections, links, result.errors, scoped=section is not None)
    if not metadata_only and result.ok:
        _compile_blocks(blocks, compiler or os.environ.get('CXX', 'clang++'), result, compile_timeout)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=Path(os.environ.get('VERIFY_ROOT', Path(__file__).resolve().parents[1])))
    parser.add_argument('--section', help='nazwa katalogu działu, np. 01_wprowadzenie lub zaawansowane')
    parser.add_argument('--metadata-only', action='store_true', help='sprawdź treść i linki bez kompilacji')
    parser.add_argument('--metrics', action='store_true', help='wypisz metryki i błędy jako JSON')
    parser.add_argument('--compiler', default=os.environ.get('CXX', 'clang++'), help='program kompilatora C++23')
    args = parser.parse_args(argv)
    result = validate(args.root, section=args.section, metadata_only=args.metadata_only, compiler=args.compiler)
    if args.metrics:
        print(json.dumps(result.as_dict(), ensure_ascii=False))
    elif result.ok:
        print(f"Markdown: {result.metrics['markdown_files']} plików; bloki C++23: {result.metrics['cpp_blocks']}; "
              f"skompilowane: {result.metrics['compiled_blocks']}; wynik: OK")
    if result.errors:
        print('\n'.join(result.errors), file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
