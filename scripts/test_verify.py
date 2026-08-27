from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify.sh"


def run_verifier(chapter: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="kompendium-cpp-test-") as temp:
        root = Path(temp)
        chapter_dir = root / "01_test"
        chapter_dir.mkdir()
        (root / "README.md").write_text("# Test\n", encoding="utf-8")
        (chapter_dir / "01_rozdzial.md").write_text(chapter, encoding="utf-8")
        env = {**os.environ, "VERIFY_ROOT": str(root)}
        return subprocess.run(
            ["bash", str(VERIFY_SCRIPT)],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )


class VerifyContentDepthTests(unittest.TestCase):
    def test_rejects_main_chapter_below_prose_word_limit(self) -> None:
        result = run_verifier(
            """[← Spis treści](../README.md)

# Krótki rozdział

Krótki opis.

~~~cpp
int main() {}
~~~

## Powiązane tematy
"""
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Za mało słów prozy", result.stderr)

    def test_rejects_main_chapter_without_depth_sections(self) -> None:
        result = run_verifier(
            "[← Spis treści](../README.md)\n\n"
            "# Rozdział bez pogłębienia\n\n"
            + ("wyjaśnienie mechanizmu decyzji kontraktu wartości zasobu " * 90)
            + "\n\n~~~cpp\nint main() {}\n~~~\n\n"
            "## Powiązane tematy\n"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Brak sekcji pogłębienia", result.stderr)

    def test_rejects_main_chapter_with_only_one_example_block(self) -> None:
        result = run_verifier(
            "[← Spis treści](../README.md)\n\n"
            "# Rozdział z jednym przykładem\n\n"
            + ("wyjaśnienie mechanizmu decyzji kontraktu wartości zasobu " * 90)
            + "\n\n## Jak to działa krok po kroku\n\nOpis.\n\n"
            "## Pogłębienie mechanizmu\n\nOpis.\n\n"
            "~~~cpp\nint main() {}\n~~~\n\n"
            "## Drugi przykład\n\nOpis bez bloku.\n\n"
            "## Porównanie i decyzje\n\nOpis.\n\n"
            "## Powiązane tematy\n"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Za mało bloków przykładów", result.stderr)


if __name__ == "__main__":
    unittest.main()
