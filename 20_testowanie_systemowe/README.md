[← Główny spis treści](../README.md)

# 20. Testowanie systemowe

Celem działu jest zaprojektować strategię testów od szybkiej domeny po granice procesu, sieci, plików i bazy. Materiał prowadzi od modelu i granic przez implementację, testy oraz decyzje operacyjne. Każdy rozdział oddziela gwarancje standardu od zachowania platformy lub narzędzia i kończy się kryteriami wyboru.

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

1. [Strategia i piramida testów](01_strategia_i_piramida_testow.md)
2. [Testy integracyjne i E2E](02_testy_integracyjne_i_e2e.md)
3. [Testy kontraktowe](03_testy_kontraktowe.md)
4. [Fake mock stub i seams](04_fake_mock_stub_i_seams.md)
5. [Fixtures builders i dane testowe](05_fixtures_builders_i_dane_testowe.md)
6. [Flaky tests i testy niefunkcjonalne](06_flaky_tests_i_testy_niefunkcjonalne.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Zasada przewodnia

Catch2 i GoogleTest są zewnętrznymi przykładami. Czas, losowość i I/O wprowadzamy przez jawne seams, aby scenariusze pozostawały deterministyczne.

## Jak pracować

Czytaj po kolei, a każdy model sprawdzaj na małym projekcie ćwiczeniowym. Zapisuj wersję toolchainu, polecenie reprodukcji i oczekiwany wynik. Nie eksperymentuj na ważnych danych ani usługach. Po rozdziale dodaj jeden test błędu i krótką kartę decyzji opisującą przyjęty kompromis.

## Źródło bazowe

Punktem odniesienia jest [GoogleTest User’s Guide](https://google.github.io/googletest/). Dokumentacja źródłowa ma pierwszeństwo przed zapamiętaną składnią, szczególnie dla opcji zmieniających się między wydaniami.
