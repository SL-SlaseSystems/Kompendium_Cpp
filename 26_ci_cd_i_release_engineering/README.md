[← Główny spis treści](../README.md)

# 26. CI/CD i release engineering

Celem działu jest przeprowadzić zmianę od commitu przez bramki jakości do podpisanego artefaktu, wdrożenia i rollbacku. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

## Wymagania wstępne

Przed rozpoczęciem warto znać RAII, typowane błędy, podstawy testowania, CMake oraz pracę z repozytorium. Gdy rozdział używa systemu lub biblioteki zewnętrznej, traktuje ją jako jawne rozszerzenie, a nie część ISO C++.

## Efekty uczenia się

- modelujesz sukces, błąd, limit i częściowe wykonanie;
- rozdzielasz mechanizm od polityki aplikacji;
- projektujesz ownership i cleanup przed implementacją;
- dobierasz testy do ryzyka oraz granicy systemu;
- zapisujesz obserwowalne kryteria decyzji;
- weryfikujesz opcje narzędzia w źródle właściwym dla używanej wersji.

## Kolejność rozdziałów

1. [Pipeline build test analyze](01_pipeline_build_test_analyze.md)
2. [Macierze kompilatorów i platform](02_macierze_kompilatorow_i_platform.md)
3. [Quality gates i cache](03_quality_gates_i_cache.md)
4. [Artefakty SBOM i podpisy](04_artefakty_sbom_i_podpisy.md)
5. [Wersjonowanie changelog i release](05_wersjonowanie_changelog_i_release.md)
6. [Deployment rollback i hotfix](06_deployment_rollback_i_hotfix.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Koncepcje pozostają neutralne względem dostawcy. Przykład GitHub Actions nie udaje standardu, a macierz GCC, Clang i MSVC nie zakłada wspólnego ABI.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [GitHub Actions documentation](https://docs.github.com/en/actions). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
