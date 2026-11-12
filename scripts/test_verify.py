from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.verify_content import parse_markdown, validate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = PROJECT_ROOT / 'scripts' / 'verify.sh'
SECTION = '01_test'


def complete_chapter(*, nav: str = '[← Spis treści](../README.md)', words: int = 510) -> str:
    """Hand-constructed prose fixture, independent of the validator's word counter."""
    return (nav + '\n\n# Rozdział\n\n' + 'wyjaśnienie ' * words
            + '\n\n## Jak to działa krok po kroku\n\nOpis.\n\n'
            '## Pogłębienie mechanizmu\n\nOpis.\n\n'
            '~~~cpp\nint main() {}\n~~~\n\n'
            '## Drugi przykład\n\n~~~cpp\nint main() { return 0; }\n~~~\n\n'
            '## Porównanie i decyzje\n\nOpis.\n\n'
            '## Powiązane tematy\n\n[Mapa](README.md)\n')


class VerifyContentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix='kompendium-cpp-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('README.md', f'# Test\n\n[Mapa]({SECTION}/README.md)\n[Temat]({SECTION}/01_rozdzial.md)\n')
        self.add_section(SECTION)

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def add_section(self, section: str, *, words: int = 510) -> None:
        self.write(f'{section}/README.md', '# Mapa\n\n[Temat](01_rozdzial.md)\n[Zadania](ZESTAW-CWICZEN.md)\n')
        self.write(f'{section}/01_rozdzial.md', complete_chapter(words=words))
        self.write(f'{section}/ZESTAW-CWICZEN.md', '# Zadania\n\nRozwiąż zadanie.\n')

    def run_verifier(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(['sh', str(VERIFY_SCRIPT), *args], text=True, capture_output=True,
                              env={**os.environ, 'VERIFY_ROOT': str(self.root), **(env or {})},
                              check=False, timeout=30)

    def assert_ok(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_old_minimal_main_chapter(self) -> None:
        self.write(f'{SECTION}/01_rozdzial.md', '[← Spis treści](../README.md)\n\n# Temat\n\nKrótki opis.\n\n~~~cpp\nint main() {}\n~~~\n\n## Powiązane tematy\n')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Za mało słów prozy', result.stderr)

    def test_rejects_main_chapter_without_exact_depth_sections(self) -> None:
        self.write(f'{SECTION}/01_rozdzial.md', complete_chapter().replace('## Pogłębienie mechanizmu', '## Pogłębienie mechanizmu dodatkowo'))
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Brak sekcji pogłębienia', result.stderr)

    def test_rejects_main_chapter_with_one_example(self) -> None:
        self.write(f'{SECTION}/01_rozdzial.md', complete_chapter().replace('~~~cpp\nint main() { return 0; }\n~~~', 'Opis bez bloku.'))
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Za mało bloków przykładów', result.stderr)

    def test_accepts_complete_chapter_and_short_worksheet(self) -> None:
        self.assert_ok(self.run_verifier('--metadata-only'))

    def test_accepts_map_navigation_with_any_label(self) -> None:
        self.write(f'{SECTION}/01_rozdzial.md', complete_chapter(nav='[← Mapa działu](README.md) · [Główny spis treści](../README.md)'))
        self.assert_ok(self.run_verifier('--metadata-only'))

    def test_rejects_missing_first_line_navigation(self) -> None:
        self.write(f'{SECTION}/01_rozdzial.md', complete_chapter(nav='# Tytuł'))
        result = self.run_verifier('--metadata-only')
        self.assertIn('Brak linku powrotnego', result.stderr)
        self.assertNotEqual(result.returncode, 0)

    def test_related_topics_must_be_final_section(self) -> None:
        self.write(f'{SECTION}/01_rozdzial.md', complete_chapter() + '\n## Dalsza treść\n\nOpis.\n')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Powiązane tematy', result.stderr)

    def test_expert_chapter_requires_650_prose_words(self) -> None:
        self.add_section('zaawansowane', words=600)
        result = self.run_verifier('--section', 'zaawansowane', '--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('minimum 650', result.stderr)
        self.write('zaawansowane/01_rozdzial.md', complete_chapter(words=660))
        self.assert_ok(self.run_verifier('--section', 'zaawansowane', '--metadata-only'))

    def test_short_exercises_and_practice_are_not_chapters(self) -> None:
        self.write('cwiczenia/01_zadanie.md', '# Ćwiczenie\n\nZadanie.\n')
        self.write('praktyka/01_projekt/README.md', '# Projekt\n\nZadanie.\n')
        self.assert_ok(self.run_verifier('--metadata-only'))

    def test_rejects_missing_local_link(self) -> None:
        self.write('notatki.md', '# Notatki\n\n[brak](nie-ma.md)\n')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Martwy link', result.stderr)

    def test_rejects_link_outside_repository(self) -> None:
        self.write('notatki.md', '# Notatki\n\n[poza](../poza.md)\n')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Link poza projektem', result.stderr)

    def test_missing_main_index_chapter_is_reported(self) -> None:
        self.write('README.md', f'# Test\n\n[Mapa]({SECTION}/README.md)\n')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Brak rozdziału w głównym indeksie', result.stderr)

    def test_missing_main_index_map_is_reported(self) -> None:
        self.write('README.md', f'# Test\n\n[Temat]({SECTION}/01_rozdzial.md)\n')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Brak mapy w głównym indeksie', result.stderr)

    def test_section_map_must_list_chapter_and_worksheet(self) -> None:
        self.write(f'{SECTION}/README.md', '# Mapa\n')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Brak rozdziału w mapie', result.stderr)
        self.assertIn('Brak zestawu ćwiczeń w mapie', result.stderr)

    def test_numbered_section_requires_map_and_worksheet(self) -> None:
        (self.root / SECTION / 'README.md').unlink()
        (self.root / SECTION / 'ZESTAW-CWICZEN.md').unlink()
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Brak mapy działu', result.stderr)
        self.assertIn('Brak zestawu ćwiczeń', result.stderr)

    def test_fences_and_inline_code_do_not_contribute_links_or_required_headings(self) -> None:
        chapter = complete_chapter().replace('## Pogłębienie mechanizmu', '~~~text\n## Pogłębienie mechanizmu\n[brak](nie-ma.md)\n~~~')
        self.write(f'{SECTION}/01_rozdzial.md', chapter + '\n`[brak](nie-ma.md)`\n')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Brak sekcji pogłębienia', result.stderr)
        self.assertNotIn('Martwy link', result.stderr)

    def test_reference_image_and_encoded_links_are_checked(self) -> None:
        self.write('obraz ze spacją.png', 'image fixture')
        self.write('notatki.md', '# Notatki\n\n[opis][cel]\n![obraz](obraz%20ze%20spacj%C4%85.png "opis")\n\n[cel]: nie-ma.md\n')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('nie-ma.md', result.stderr)
        self.assertNotIn('obraz%20', result.stderr)

    def test_remote_links_and_local_fragments_are_accepted(self) -> None:
        self.write('notatki.md', '# Notatki\n\n[web](https://example.invalid/brak)\n[email](mailto:test@example.invalid)\n[fragment](#notatki)\n')
        self.assert_ok(self.run_verifier('--metadata-only'))

    def test_unclosed_fence_invalid_utf8_and_empty_markdown_are_reported(self) -> None:
        self.write('puste.md', ' \n')
        self.write('fence.md', '# Kod\n\n````cpp\nint main() {}\n```\n')
        (self.root / 'utf8.md').write_bytes(b'\xff\xfe')
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Pusty plik', result.stderr)
        self.assertIn('Niedomknięty blok kodu', result.stderr)
        self.assertIn('UTF-8', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_excluded_directories_and_symlink_directories_are_not_read(self) -> None:
        for folder in ('.git', '__pycache__', 'build', 'cmake-build-debug', 'docs/superpowers'):
            self.write(f'{folder}/bad.md', '')
        with tempfile.TemporaryDirectory(prefix='kompendium-external-') as external:
            (Path(external) / 'bad.md').write_text('', encoding='utf-8')
            (self.root / 'symlinked').symlink_to(external, target_is_directory=True)
            self.assert_ok(self.run_verifier('--metadata-only'))

    def test_metrics_count_selected_markdown_types_and_compilable_blocks(self) -> None:
        self.add_section('zaawansowane', words=660)
        with (self.root / 'README.md').open('a', encoding='utf-8') as stream:
            stream.write('\n[Expert](zaawansowane/01_rozdzial.md)\n[Mapa expert](zaawansowane/README.md)\n')
        self.write('praktyka/README.md', '# Praktyka\n\n~~~cpp,notest\ninvalid C++\n~~~\n')
        result = self.run_verifier('--metadata-only', '--metrics')
        self.assert_ok(result)
        metrics = json.loads(result.stdout)
        self.assertEqual({key: metrics[key] for key in ('markdown_files', 'main_chapters', 'expert_chapters', 'cpp_blocks', 'section_maps', 'exercise_sets', 'errors')}, {
            'markdown_files': 8, 'main_chapters': 1, 'expert_chapters': 1,
            'cpp_blocks': 4, 'section_maps': 2, 'exercise_sets': 2, 'errors': [],
        })

    def test_metrics_include_validation_errors(self) -> None:
        self.write('notatki.md', '')
        result = self.run_verifier('--metadata-only', '--metrics')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stdout.lstrip().startswith('{'), result.stdout)
        self.assertTrue(any('Pusty plik' in error for error in json.loads(result.stdout)['errors']))

    def test_section_filter_does_not_require_complete_root_index_or_other_content(self) -> None:
        self.add_section('02_inny')
        self.write('README.md', '# Niepełny indeks\n')
        self.write('02_inny/01_rozdzial.md', '')
        result = self.run_verifier('--section', SECTION, '--metadata-only', '--metrics')
        self.assert_ok(result)
        metrics = json.loads(result.stdout)
        self.assertEqual(metrics['markdown_files'], 3)
        self.assertEqual(metrics['main_chapters'], 1)

    def test_unknown_or_escaping_section_is_an_error(self) -> None:
        for section in ('nieznany', '../', '/tmp'):
            with self.subTest(section=section):
                result = self.run_verifier('--section', section, '--metadata-only')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Nieznany dział', result.stderr)

    def test_metadata_only_does_not_need_compiler(self) -> None:
        self.assert_ok(self.run_verifier('--metadata-only', env={'CXX': '/nieistniejacy/compiler'}))

    def test_default_mode_compiles_cpp_without_running_programs_and_skips_notest(self) -> None:
        chapter = complete_chapter().replace('int main() {}', 'int main() { throw "never execute me"; }')
        self.write(f'{SECTION}/01_rozdzial.md', chapter + '\n~~~cpp,notest\ninvalid C++\n~~~\n')
        self.assert_ok(self.run_verifier())

    def test_default_mode_reports_cpp_syntax_error_and_compiler_override(self) -> None:
        self.write(f'{SECTION}/01_rozdzial.md', complete_chapter().replace('int main() {}', 'this is invalid C++;'))
        result = self.run_verifier('--compiler', '/usr/bin/clang++', env={'CXX': '/nieistniejacy/compiler'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Błąd przykładu', result.stderr)
        self.assertIn('01_rozdzial.md:', result.stderr)

    def test_compiler_failure_is_reported_without_traceback(self) -> None:
        result = self.run_verifier(env={'CXX': '/nieistniejacy/compiler'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Nie znaleziono kompilatora', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_cpp_source_retains_link_shaped_text_without_checking_it_as_prose(self) -> None:
        self.write(f'{SECTION}/01_rozdzial.md', complete_chapter().replace(
            'int main() {}', 'const char* label = "[nie](nie-ma.md)";\nint main() { return label[0] == 0; }'))
        self.assert_ok(self.run_verifier())

    def test_prose_word_limit_does_not_count_fenced_code(self) -> None:
        chapter = complete_chapter(words=10).replace('int main() {}', '// ' + 'wyjaśnienie ' * 700 + '\nint main() {}')
        self.write(f'{SECTION}/01_rozdzial.md', chapter)
        result = self.run_verifier('--metadata-only')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Za mało słów prozy', result.stderr)

    def test_remote_readme_is_not_local_chapter_navigation(self) -> None:
        for target in ('https://example.invalid/README.md', 'mailto:README.md'):
            with self.subTest(target=target):
                self.write(f'{SECTION}/01_rozdzial.md', complete_chapter(nav=f'[Mapa]({target})'))
                result = self.run_verifier('--metadata-only')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Brak linku powrotnego', result.stderr)

    def test_indented_code_does_not_create_local_links(self) -> None:
        self.write('notatki.md', '# Notatki\n\n    [kod](nie-ma.md)\n\n\t[kod](drugi-brak.md)\n')
        self.assert_ok(self.run_verifier('--metadata-only'))

    def test_cpp_fence_parser_preserves_shorter_fences_inside_longer_fence(self) -> None:
        parsed = parse_markdown('````cpp\n// [kod](brak.md)\n```\n````\n\n[proza](README.md)\n')
        self.assertEqual([(link.line, link.target) for link in parsed.links], [(6, 'README.md')])
        self.assertEqual([(block.line, block.info, block.code) for block in parsed.blocks], [(1, 'cpp', '// [kod](brak.md)\n```\n')])
        self.assertIsNone(parsed.unclosed_fence)

    def test_public_api_reports_compiler_timeout_instead_of_hanging(self) -> None:
        compiler = self.write('slow compiler', f'#!{sys.executable}\nimport time\ntime.sleep(1)\n')
        compiler.chmod(0o755)
        result = validate(self.root, compiler=str(compiler), compile_timeout=0.05)
        self.assertFalse(result.ok)
        self.assertTrue(any('Przekroczono czas kompilacji' in error for error in result.errors))
        self.assertEqual(result.metrics['compiled_blocks'], 0)

    def test_compiler_receives_cpp23_thread_and_warning_options_as_arguments(self) -> None:
        compiler = self.write('compiler with spaces;no shell', f'#!{sys.executable}\nimport sys\nrequired = {{"-std=c++23", "-pthread", "-Wall", "-Wextra", "-Wpedantic", "-fsyntax-only"}}\nsys.exit(0 if required.issubset(sys.argv[1:]) and len(sys.argv[1:]) == 7 else 5)\n')
        compiler.chmod(0o755)
        self.assert_ok(self.run_verifier('--compiler', str(compiler)))

    def test_direct_cli_root_overrides_environment(self) -> None:
        result = subprocess.run([sys.executable, str(PROJECT_ROOT / 'scripts' / 'verify_content.py'),
                                 '--root', str(self.root), '--metadata-only'],
                                text=True, capture_output=True, check=False,
                                env={**os.environ, 'VERIFY_ROOT': '/nieistniejacy'}, timeout=30)
        self.assert_ok(result)


if __name__ == '__main__':
    unittest.main()
